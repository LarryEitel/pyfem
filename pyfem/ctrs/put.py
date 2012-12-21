# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
import mdls
from mdls import *

class Put(object):

    def __init__(self, g):
        #: Doc comment for instance attribute db
        self.g = g
        self.usr = g['usr']
        self.db  = g['db']
        #self.es  = g['es']

    def put(self, _cls, query, update, **kwargs):
        debug    = self.g['logger'].debug
        db       = self.db

        mCls       = getattr(mdls, _cls)
        collNam    = mCls._collection.name
        coll       = mCls._collection

        response   = {}
        status     = 200

        # fields to get from baseDoc find
        baseFldNams = [['_id'], ['oBy'], ['oOn'], ['oAt']]

        # get fldNams targeted for update
        fldNams = []
        for action, flds in update['actions'].iteritems():
            for fld in flds['flds']:
                fldNams.append(fld.split('.'))

        baseFldNams += fldNams

        # Note that we are limiting updates to ONE doc at this time
        # default targetDoc to baseDoc, may end up being an embedded doc
        targetDoc = baseDoc = coll.find_one(query = query, fields = [fld[0] for fld in baseFldNams])

        targetDocCls = getattr(mdls, _cls)

        # check if targetDoc is already locked. What to do?
        # if locked, retry for x secs
        # if unsuccessful, return error

        # lock target doc
        doc = coll.find_and_modify(
            query = query,
            update = {'$set': {'locked': True}},
            new = True
        )

        # are any of them involved in generating dNam/dNamS?
        updateLnks = False
        if hasattr(targetDocCls, '_meta') and 'fldsThatUpdt_dNam' in targetDocCls._meta:
            dNamFlds = set(targetDocCls._meta['fldsThatUpdt_dNam'])
            fldsThatUpdt_dNam = [fld for i, fld in enumerate(fldNams) if fld in dNamFlds]
            updateLnks = len(fldsThatUpdt_dNam) > 0


        # validate actions and update values to be put/patched to the targetDoc
        errors = {}
        patchActions = {}
        fldCls = None
        for a, action in enumerate(update['actions']):
            flds = update['actions'][action]['flds']

            if action == '$push':
                # hackage here
                # need to create a fake parent doc to hold the items that will be added.
                # if there is an _eIds, grab it cause we will use it
                # link to items to be added so that they can be validated
                proxyTargetDoc = {}

                # add items to be added to proxy so we can validate, etc
                for fld, fldItems in flds.iteritems():
                    proxyTargetDoc[fld] = fldItems

                fldUpdates = {}

                # need to set eIds for items to be added
                # what about when items are to be added to existing list WITH eId's?
                proxyFld = proxyTargetDoc[fld]

                # does this put/patch involve a link to another doc?
                if fld == 'pars':
                    # add a pth/path to pars means enough details were provided in update to get details regarding the doc to be linked to
                    # while on Prs.sue, if user wants to add a parent link to Prs.bill as father
                    # this will require locking and updating two docs

                    srcLnk      = proxyTargetDoc[fld][0]['lnk']
                    target_cls  = srcLnk['doc_cls']
                    targetClass = getattr(mdls, target_cls)
                    targetSlug  = srcLnk['slug']
                    target      = coll.find_one(query = {'slug': targetSlug})

                    lnkRelSlug = srcLnk['lnkRelSlug']

                    pass
                if fld == 'chlds':
                    pass


                doc_errors = []

                attrPath = []
                # need to validate docs
                recurseDoc(proxyTargetDoc, fld, proxyTargetDoc, recurseValidate, attrPath, doc_errors)
                if doc_errors:
                    break

                # run listField.validateList against the existing AND proposed additions
                if '_cls' in proxyTargetDoc[fld][0]:
                    targetListItem_cls = proxyTargetDoc[fld][0]['_cls']
                    targetListItem = getattr(mdls, targetListItem_cls)(**proxyTargetDoc[fld][0])
                    errors = targetListItem.validateList(targetDoc[fld] + proxyTargetDoc[fld])
                    if errors:
                        error = {'attrPath': fld, 'fld':fld, 'errors': errors}
                        doc_errors.append(error)
                        break

                listItemsToAdd = []
                for i, item in enumerate(proxyFld):
                    listItemsToAdd.append(item)

                # if only one item use default $push and send one item
                if len(listItemsToAdd) == 1:
                    fldUpdates[fld] = listItemsToAdd[0]
                else:
                    # if more than one item use $pushAll and send list of items to insert
                    action = '$pushAll'
                    fldUpdates[fld] = listItemsToAdd

                patchActions[action] = fldUpdates
                if not '$set' in patchActions:
                    patchActions['$set'] = {}

            else:
                fldUpdates = {}
                for fld, val in flds.iteritems():
                    # need to validate val
                    # targetNote is the dict of the doc containing the field to update
                    fldCls = getattr(targetDocCls, fld.split('.')[0])

                    doc_errors = []
                    attrPath = []
                    recurseDoc(targetDoc, fld, targetDoc, recurseValidate, attrPath, doc_errors)

                    if doc_errors:
                        return doc_errors

                    if hasattr(fldCls, 'myError'):
                        errors[fld] = fldCls.myError
                        flds[fld] = {'val': val, 'error': fldCls.myError}
                        break

                    targetDoc[fld] = val

                    fldUpdates[fld] = val

                patchActions[action] = fldUpdates


        if doc_errors:
            response['errors']        = doc_errors
            status                    = 500
        else:

            # need to include fldUpdate to unlock targetDoc
            if not '$unset' in patchActions:
                patchActions['$unset'] = {}

            patchActions['$unset']['locked'] = True

            # need to log change
            #resp = mdls.logit(self.usr, baseDoc, targetDoc)
            #updtFlds = resp['response']['updtFlds']
            #if updtFlds:
                #if not '$set' in patchActions:
                    #patchActions['$set'] = {}
                #for fld, val in updtFlds.iteritems():
                    #patchActions['$set'][fld] = val


            doc = coll.find_and_modify(
                query = query,
                update = patchActions,
                new = True
            )

            # TODO: Handle condition when doc == None

            response['_id'] = doc['_id']
            response['OID'] = doc['_id'].__str__()
            response['doc'] = doc

        return {'response': response, 'status': status}