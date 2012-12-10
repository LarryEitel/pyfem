# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import models
import globals
import models
from models import *

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

        mCls       = getattr(models, _cls)
        collNam    = mCls._collection.name
        coll       = mCls._collection

        response   = {}
        status     = 200

        # fields to get from baseDoc find
        baseFldNams = ['_id', 'oBy', 'oOn', 'oAt']

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
            # need to convert eId to offset notation
            # used by pymongo to reach in to a subdoc
            docFld = baseDoc[baseFldNam]
            for seg in target_eIdPathSegs:
                if not seg.isdigit():
                    target_offsetPath.append(seg)
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

                    target_offsetPath.append(str(offset))

            # init the class for targetDoc
            targetDocCls = getattr(models, targetDoc['_cls'])
        else:
            targetDocCls = getattr(models, _cls)

        # check if targetDoc is already locked. What to do?
        # if locked, retry for x secs
        # if unsuccessful, return error

        # lock target doc
        qryDat = {'slug': 'LarryStooge'}
        doc = coll.find_and_modify(
            query = qryDat,
            update = {'$set': {'.'.join(target_offsetPath + ['locked']): True}},
            new = True
        )



        # are any of them involved in generating dNam/dNamS?
        updateLnks = False
        if 'fldsThatUpdt_dNam' in targetDocCls._meta:
            dNamFlds = set(targetDocCls._meta['fldsThatUpdt_dNam'])
            fldsThatUpdt_dNam = [fld for i, fld in enumerate(fldNams) if fld in dNamFlds]
            updateLnks = len(fldsThatUpdt_dNam) > 0



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

                doc_errors = []
                attrPath = []
                recurseDoc(targetDoc, fld, targetDoc, recurseValidate, attrPath, doc_errors)

                if doc_errors:
                    return doc_errors


                # fldCls.validate(val)

                # TODO: need to consider my recurse function here because it validate more than just top level replacement value. The value can be itself a nest doc
                if hasattr(fldCls, 'myError'):
                    errors[fld] = fldCls.myError
                    flds[fld] = {'val': val, 'error': fldCls.myError}
                else:
                    targetDoc[fld] = val
                    fldUpdates['.'.join(target_offsetPath + [fld])] = val
            patchActions[action] = fldUpdates

        # need to include fldUpdate to unlock targetDoc
        if not '$unset' in patchActions:
            patchActions['$unset'] = {}

        patchActions['$unset']['.'.join(target_offsetPath + ['locked'])] = True

        # need to log change
        resp = models.logit(self.usr, baseDoc, targetDoc)
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


        response['_id'] = doc['_id']
        response['OID'] = doc['_id'].__str__()
        response['doc'] = doc

        return {'response': response, 'status': status}