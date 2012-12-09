# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import models
import globals
import models

class GenericPut(object):

    def __init__(self, g):
        #: Doc comment for instance attribute db
        self.usr = g['usr']
        self.db  = g['db']
        #self.es  = g['es']

    def put(self, **kwargs):
        """patch a doc"""
        db       = self.db

        _cls     = kwargs['_cls']
        qryDat   = kwargs['query']
        patchDat = kwargs['update']

        mCls = getattr(models, _cls)
        collNam    = mCls._collection.name
        coll       = mCls._collection

        response   = {}
        status     = 200

        # ie, emails.2.notes.1
        # split
        eIdPath = patchDat['docPath'].split('.')

        # first seg will be the primary field name that we are focused on
        # ie, emails
        primFldNam = eIdPath[0]

        # get doc with emails parent doc
        # for convenience, lets get _id in case another query was used
        # Note that we are limiting updates to ONE doc at this time
        doc = coll.find_one(query = qryDat, fields = ['_id', primFldNam])

        # need to convert eId to offset notation
        # used by pymongo to reach in to a subdoc
        docFld = doc[primFldNam]
        targetDoc = doc
        offsetPath = []
        for seg in eIdPath:
            if not seg.isdigit():
                offsetPath.append(seg)
                targetDoc = targetDoc[seg]
            else:
                eId = int(seg)
                offset = -1
                for i, item in enumerate(targetDoc):
                    if item['eId'] == eId:
                        offset = i
                        targetDoc = targetDoc[i]
                        break

                if offset == -1:
                    raise Exception('Failed to find eId in list')

                offsetPath.append(str(offset))

        targetPath   = '.'.join(offsetPath)
        targetDocCls = getattr(models, targetDoc['_cls'])

        # get fldNams targeted for patchDat
        fldNams = []
        for action, flds in patchDat['actions'].iteritems():
            for fld in flds['flds']:
                fldNams.append(fld)

        # are any of them involved in generating dNam/dNamS?
        updateLnks = False
        if 'fldsThatUpdt_dNam' in targetDocCls._meta:
            dNamFlds = set(targetDocCls._meta['fldsThatUpdt_dNam'])
            fldsThatUpdt_dNam = [fld for i, fld in enumerate(fldNams) if fld in dNamFlds]
            updateLnks = len(fldsThatUpdt_dNam) > 0


        # lock target doc
        qryDat = {'slug': 'LarryStooge'}
        doc = coll.find_and_modify(
            query = qryDat,
            update = {'$set': {targetPath + '.locked': True}},
            new = True
        )

        # validate actions and update values to be put/patched to the targetDoc
        errors = {}
        patchActions = {}
        for a, action in enumerate(patchDat['actions']):
            flds = patchDat['actions'][action]['flds']
            fldUpdates = {}
            for fld, val in flds.iteritems():
                # need to validate val
                # targetNote is the dict of the doc containing the field to update
                fldCls = getattr(targetDocCls, fld)
                fldCls.validate(val)
                if hasattr(fldCls, 'myError'):
                    errors[fld] = fldCls.myError
                    flds[fld] = {'val': val, 'error': fldCls.myError}
                else:
                    targetDoc[fld] = val
                    fldUpdates[targetPath + '.' + fld] = val
            patchActions[action] = fldUpdates

        # need to include fldUpdate to unlock targetDoc
        if not '$unset' in patchActions:
            patchActions['$unset'] = {}

        patchActions['$unset'][targetPath + '.locked'] = True

        # need to log change

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
                patchActions['$set'][targetPath + '.dNam'] = targetDoc['dNam']
            if 'dNamS' in targetDoc:
                patchActions['$set'][targetPath + '.dNamS'] = targetDoc['dNamS']


        doc = coll.find_and_modify(
            query = qryDat,
            update = patchActions,
            new = True
        )


        # need to get base doc/sub-doc in order to validate, update eId's, logit etc
        # although very brief, need to lock doc/sub-doc just in case of a race.
        qryDat = {'slug': 'LarryStooge'}
        doc = coll.find_and_modify(
            query = qryDat,
            update = {'$set': {'locked': True}},
            new = True
        )
        doc = coll.find_one(
            query = qryDat,
            fields = ['emails']
        )

        # need to validate submitted values
        errors = {}
        for fldNam in fldNams:
            fldCls = getattr(mCls, fldNam)
            if 'fld' in patchDat['flds'][fldNam]:
                fldMember = fldCls.field.lookup_member(patchDat['flds'][fldNam]['fld'])
            else:
                fldMember = fldCls.field.lookup_member(fldNam)

            fldMember.validate(patchDat['flds'][fldNam]['val'])
            if hasattr(fldMember, 'myError'):
                errors[fldNam] = fldMember.myError
                patchDat['flds'][fldNam]['error'] = fldMember.myError

        # handle errors
        if errors:
            response['errors'] = errors
            response['patchDat'] = patchDat
            return {'response': response, 'status': 400}

        # build find_and_modify patchDat params
        fldsToUpdt = {}
        for fldNam in fldNams:
            fld = patchDat['flds'][fldNam]
            fldsToUpdt[fld['pos']] = fld['val']

        # If so, need to check for an tos/frs to traverse since they contain refs to this dNam

        # need to log patchDat
        # need to increment eId if list item
        doc = coll.find_and_modify(
            query = qryDat,
            update = {patchDat['cmd']: fldsToUpdt},
            new = True
        )
        #query = {'slug': 'LarryStooge', 'emails.eId':2}
        #patchDat = {'$set': {'emails.$.typ': 'fun'}}
        #doc = coll.find_and_modify(
            #query = query,
            #patchDat = patchDat,
            #new = True
        #)
        response['_id'] = doc['_id']
        response['OID'] = doc['_id'].__str__()
        response['doc'] = doc

        return {'response': response, 'status': status}
        x=0


        # # if element eId was passed, expect to put/patch change to one element in a Listfld
        # if eId and len(patch) == 1:
        #     elem    = patch.popitem()
        #     attrNam = elem[0]

        #     # enhance to support putting/updating multiple list elements
        #     attrVal = elem[1][0]

        #     resp    = preSave(attrVal, self.usr)
        #     if not resp['status'] == 200:
        #         return {'response': resp, 'status': 400}

        #     attrVal = resp['response']['doc']
        #     # http://docs.mongodb.org/manual/applications/patchDat/
        #     # patch patchDat in tmp collection
        #     attrEl = attrNam + '.$'
        #     doc = collTmp.find_and_modify(
        #         query = where,
        #         patchDat = { "$set": { attrEl: attrVal }},
        #         new = True
        #     )
        #     response['collection'] = collNamTmp
        #     response['total_invalid'] = 0
        #     response['id'] = id.__str__()

        #     # remove this, not needed
        #     response['doc'] = doc

        #     return {'response': response, 'status': 200}
        # else:
        #     # validate patch
        #     # init mCls for this doc
        #     patch_errors = validate_partial(mCls, patch)
        #     if patch_errors:
        #         response['errors'] = patch_errors['errors']
        #         response['total_errors'] = patch_errors['count']
        #         status = 500

        #         return prep_response(response, status = status)

        #     # logit patchDat
        #     patch = logit(self.usr, patch)

        #     # patch patchDat in tmp collection
        #     doc = collTmp.find_and_modify(
        #         query = where,
        #         patchDat = {"$set": patch},
        #         new = True
        #     )

        # # init model instance
        # model      = mCls(**doc)

        # response['total_invalid'] = 0
        # response['id'] = id.__str__()

        # return {'response': response, 'status': status}
