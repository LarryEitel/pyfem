# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
import ctrs
from mdls import *
from mdls.helpers import *

class Put(object):
    def cmd(self, cmd):
        g = app.g
        debug = g['logger'].debug
        post    = ctrs.post.Post().post
        put     = ctrs.put.Put().put
        fldClss = g['fldClss']

        debug(u'\n' + (u'_'*50) + u'\n' + cmd + u'\n' + (u'_'*50))
        params = cmd.split('|')
        fn = params.pop(0)

        if fn == 'set':
            # example: 'set|Cmp|q:slug:ni,emails.address:steve@apple.com,emails.typ:work|address:bill@ms.com|typ:home'
            uri    = params.pop(0)
            _cls   = uri
            querys = params.pop(0)[2:].split(',') # strip off q: and split
            query  = dict([(v.split(':')[0],v.split(':')[1]) for v in querys])
            data   = dict(_cls=_cls, query=query)

            # get flds to set
            flds   = dict([(v.split(':')[0],
                            v.split(':')[1] if not v.split(':')[1].isdigit() else int(v.split(':')[1]))
                           for v in params])

            data['update'] = dict(actions={'$set': dict(flds=flds)})
            resp = put(**data)
            assert resp['status'] == 200
            return resp

        if fn == 'push':
            # example: 'putPush|Prs.lwe.emails|address:steve@apple.com|typ:work'
            uri = params.pop(0).split('.')
            _cls = uri[0]
            slug = uri[1]
            fld = uri[2]
            data = dict(_cls=_cls, query=dict(slug=slug))
            fldCls = fldClss[fld]

            # get flds to set
            flds = dict([(v.split(':')[0], v.split(':')[1]) for v in params])
            flds['_cls'] = fldCls
            flds['_types'] = [fldCls]

            data['update'] = dict(actions={'$push': dict(flds={fld: [flds]})})
            resp = put(**data)
            return resp


    def put(self, _cls, query, update, **kwargs):
        debug    = app.g['logger'].debug
        me       = app.me
        pymongo       = app.pymongo
        g        = app.g
        usrOID       = g['usr']['OID']

        _clss        = g['_clss']

        mCls       = getattr(mdls, _cls)
        collNam    = _clss[_cls]['collNam']
        coll       = pymongo[collNam]

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