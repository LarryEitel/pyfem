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
        #: Doc comment for instance attribute me
        self.g = g
        self.usr = g['usr']
        self.me  = g['me']
        #self.es  = g['es']

    def put(self, **kwargs):
        """patch a doc"""

        debug    = self.g['logger'].debug
        me       = self.me

        _cls     = kwargs['_cls']
        qryDat   = kwargs['query']
        patchDat = kwargs['update']

        mCls       = getattr(mdls, _cls)
        collNam    = mCls._collection.name
        coll       = mCls._collection

        response   = {}
        status     = 200

        # fields to get from baseDoc find
        baseFldNams = ['_id', '_eIds', 'eId', 'oBy', 'oOn', 'oAt', 'dNam', 'dNamS']

        # get fldNams targeted for patchDat
        fldNams = []
        for action, flds in patchDat['actions'].iteritems():
            for fld in flds['flds']:
                fldNams.append(fld)


        target_eIdPath    = patchDat['target_eIdPath']

        # will hold pymongo version of target path
        # possibly empty if updates are targeted only to baseDoc
        target_offsetPath = []

        # if no target_eIdPath, it means that fields to update are in the baseDoc
        if not target_eIdPath:
            baseFldNams += fldNams
        else:
            # ie, emails.2.notes.1
            # split
            # if no
            target_eIdPathSegs = target_eIdPath.split('.')

            # first seg will be the primary field name that we are focused on
            # ie, emails
            baseFldNam = target_eIdPathSegs[0]
            baseFldNams += [baseFldNam]

        # Note that we are limiting updates to ONE doc at this time
        # default targetDoc to baseDoc, may end up being an embedded doc
        targetDoc = baseDoc = coll.find_one(query = qryDat, fields = baseFldNams)

        if target_eIdPath:
            # need to convert eId to targetOffset notation
            # used by pymongo to reach in to a subdoc
            docFld = baseDoc[baseFldNam]

            # since target involves a ListTypeItem, need to save pointer to actual list so that we can run list-level validation
            targetList = docFld # this is the root targetList

            # traverse eIdPath
            for seg in target_eIdPathSegs:
                # if not digit, it is the name of a list field
                if not seg.isdigit():
                    target_offsetPath.append(seg)
                    targetList = targetDoc  = targetDoc[seg]
                else:
                    eId = int(seg)
                    targetOffset = -1
                    for i, item in enumerate(targetDoc):
                        if item['eId'] == eId:
                            # The last time this is set will give us the where in targetList to set changes to then validate the updated item against the entire list.
                            targetOffset = i
                            targetDoc = targetDoc[i]
                            break

                    if targetOffset == -1:
                        raise Exception('Failed to find eId in list')

                    target_offsetPath.append(str(targetOffset))

            # init the class for targetDoc
            targetDocCls = getattr(mdls, targetDoc['_cls'])
        else:
            targetDocCls = getattr(mdls, _cls)

        # check if targetDoc is already locked. What to do?
        # if locked, retry for x secs
        # if unsuccessful, return error

        # lock target doc
        doc = coll.find_and_modify(
            query = qryDat,
            update = {'$set': {'.'.join(target_offsetPath + ['locked']): True}},
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
        for a, action in enumerate(patchDat['actions']):
            flds = patchDat['actions'][action]['flds']

            if action == '$push':
                # hackage here
                # need to create a fake parent doc to hold the items that will be added.
                # if there is an _eIds, grab it cause we will use it
                # link to items to be added so that they can be validated
                proxyTargetDoc = {}

                # use existing eIds if exists
                if '_eIds' in targetDoc:
                    proxyTargetDoc['_eIds'] = targetDoc['_eIds']

                # add items to be added to proxy so we can validate, etc
                for fld, fldItems in flds.iteritems():
                    proxyTargetDoc[fld] = fldItems

                fldUpdates = {}

                # need to set eIds for items to be added
                # what about when items are to be added to existing list WITH eId's?
                proxyFld = proxyTargetDoc[fld]

                # init next_eId for this list
                next_eId = targetDoc['_eIds'][fld] if fld in targetDoc['_eIds'] else 1

                # starting with the next_eId from the existing list of items, incrementally set each eId
                for i, item in enumerate(proxyFld):
                    proxyFld[i]['eId'] = next_eId
                    next_eId += 1
                proxyTargetDoc['_eIds'][fld] = next_eId


                # does this put/patch involve a link to another doc?
                if fld == 'pars':
                    # add a pth/path to pars means enough details were provided in patchDat to get details regarding the doc to be linked to
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

                attrPath = []
                recurseDoc(proxyTargetDoc, fld, proxyTargetDoc, recurseVOnUpSert, attrPath, doc_errors)
                if doc_errors:
                    break


                # run listField.validateList against the existing AND proposed additions
                if '_cls' in proxyTargetDoc[fld][0]:
                    targetListItem_cls = proxyTargetDoc[fld][0]['_cls']
                    targetListItem = getattr(mdls, targetListItem_cls)(**proxyTargetDoc[fld][0])
                    errors = targetListItem.validateList(targetDoc[fld] + proxyTargetDoc[fld])
                    if errors:
                        error = {'attrPath': '.'.join(target_offsetPath + [fld]), 'fld':fld, 'errors': errors}
                        doc_errors.append(error)
                        break

                listItemsToAdd = []
                for i, item in enumerate(proxyFld):
                    listItemsToAdd.append(item)

                # if only one item use default $push and send one item
                if len(listItemsToAdd) == 1:
                    fldUpdates['.'.join(target_offsetPath + [fld])] = listItemsToAdd[0]
                else:
                    # if more than one item use $pushAll and send list of items to insert
                    action = '$pushAll'
                    fldUpdates['.'.join(target_offsetPath + [fld])] = listItemsToAdd

                patchActions[action] = fldUpdates
                if not '$set' in patchActions:
                    patchActions['$set'] = {}
                patchActions['$set']['.'.join(target_offsetPath + ['_eIds'])] = proxyTargetDoc['_eIds']

            else:
                fldUpdates = {}
                for fld, val in flds.iteritems():
                    # need to validate val
                    # targetNote is the dict of the doc containing the field to update
                    fldCls = getattr(targetDocCls, fld)

                    doc_errors = []
                    attrPath = []
                    recurseDoc(targetDoc, fld, targetDoc, recurseValidate, attrPath, doc_errors)

                    if doc_errors:
                        return doc_errors

                    attrPath = []
                    recurseDoc(targetDoc, fld, targetDoc, recurseVOnUpSert, attrPath, doc_errors)

                    if doc_errors:
                        return doc_errors

                    if hasattr(fldCls, 'myError'):
                        errors[fld] = fldCls.myError
                        flds[fld] = {'val': val, 'error': fldCls.myError}
                        break

                    targetDoc[fld] = val

                    if target_eIdPath:
                        targetList[targetOffset][fld] = val


                    fldUpdates['.'.join(target_offsetPath + [fld])] = val

                    if '_eIds' in targetDoc:
                        fldUpdates['.'.join(target_offsetPath + ['_eIds'])] = targetDoc['_eIds']

                # run listField.validateList against the existing AND proposed additions
                if target_eIdPath and '_cls' in targetList[0]:
                    targetListItem_cls = targetList[0]['_cls']
                    targetListItem = getattr(mdls, targetListItem_cls)(**targetList[0])
                    errors = targetListItem.validateList(targetList)
                    if errors:
                        error = {'attrPath': '.'.join(target_offsetPath + [fld]), 'fld':fld, 'errors': errors}
                        doc_errors.append(error)
                        break

                patchActions[action] = fldUpdates


        if doc_errors:
            response['errors']        = doc_errors
            status                    = 500
        else:

            # need to include fldUpdate to unlock targetDoc
            if not '$unset' in patchActions:
                patchActions['$unset'] = {}

            patchActions['$unset']['.'.join(target_offsetPath + ['locked'])] = True

            # need to log change
            resp = mdls.logit(self.usr, baseDoc, targetDoc)
            updtFlds = resp['response']['updtFlds']
            if updtFlds:
                if not '$set' in patchActions:
                    patchActions['$set'] = {}
                for fld, val in updtFlds.iteritems():
                    patchActions['$set']['.'.join(target_offsetPath + [fld])] = val

            # if targetDoc has fields that are used to generate dNam/dNamS (Display Name & Short)
            # need to fire targetDocCls.vOnUpSert() function and add dNam/dNamS to patchActions
            if updateLnks:
                resp = targetDocCls.vOnUpSert(targetDoc)
                if 'errors' in resp and resp['errors']:
                    # handle errors
                    raise Exception("Failed to run vOnUpSert")
                targetDoc = resp['doc_dict']
                if not '$set' in patchActions:
                    patchActions['$set'] = {}
                if 'dNam' in targetDoc:
                    patchActions['$set']['.'.join(target_offsetPath + ['dNam'])] = targetDoc['dNam']
                if 'dNamS' in targetDoc:
                    patchActions['$set']['.'.join(target_offsetPath + ['dNamS'])] = targetDoc['dNamS']


            doc = coll.find_and_modify(
                query = qryDat,
                update = patchActions,
                new = True
            )

            # TODO: Handle condition when doc == None

            response['_id'] = doc['_id']
            response['OID'] = doc['_id'].__str__()
            response['doc'] = doc

        return {'response': response, 'status': status}