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
        """Update a doc"""
        db = self.db

        _cls       = kwargs['_cls']
        query      = kwargs['query']
        update     = kwargs['update']

        modelClass = getattr(models, _cls)
        collNam    = modelClass._collection.name
        coll       = modelClass._collection

        response   = {}
        status     = 200

        # get fields targeted for update
        fields = [updateItem['field'] for updateItem in update if 'field' in updateItem]
        updateLnks = False
        if 'fldsThatUpdt_dNam' in modelClass._meta:
            dNamFlds = set(modelClass._meta['fldsThatUpdt_dNam'])
            fldsThatUpdt_dNam = [field for i, field in enumerate(fields) if field in dNamFlds]
            updateLnks = len(fldsThatUpdt_dNam) > 0

        x=0

        # do they impact dNam?
        # is the update val a class that needs to be validated?




        # doc = coll.find_and_modify(
        #     query = query,
        #     update = update,
        #     new = True
        # )
        # x=0


        # # if element eId was passed, expect to put/patch change to one element in a ListField
        # if eId and len(patch) == 1:
        #     elem    = patch.popitem()
        #     attrNam = elem[0]

        #     # enhance to support putting/updating multiple list elements
        #     attrVal = elem[1][0]

        #     resp    = preSave(attrVal, self.usr)
        #     if not resp['status'] == 200:
        #         return {'response': resp, 'status': 400}

        #     attrVal = resp['response']['doc']
        #     # http://docs.mongodb.org/manual/applications/update/
        #     # patch update in tmp collection
        #     attrEl = attrNam + '.$'
        #     doc = collTmp.find_and_modify(
        #         query = where,
        #         update = { "$set": { attrEl: attrVal }},
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
        #     # init modelClass for this doc
        #     patch_errors = validate_partial(modelClass, patch)
        #     if patch_errors:
        #         response['errors'] = patch_errors['errors']
        #         response['total_errors'] = patch_errors['count']
        #         status = 500

        #         return prep_response(response, status = status)

        #     # logit update
        #     patch = logit(self.usr, patch)

        #     # patch update in tmp collection
        #     doc = collTmp.find_and_modify(
        #         query = where,
        #         update = {"$set": patch},
        #         new = True
        #     )

        # # init model instance
        # model      = modelClass(**doc)

        # response['total_invalid'] = 0
        # response['id'] = id.__str__()

        # return {'response': response, 'status': status}
