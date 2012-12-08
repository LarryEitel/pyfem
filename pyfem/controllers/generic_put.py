# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import models
import globals

class GenericPut(object):

    def __init__(self, g):
        #: Doc comment for instance attribute db
        self.usr = g['usr']
        self.db  = g['db']
        #self.es  = g['es']

    def put(self, **kwargs):
        """Update a doc"""
        db = self.db
        # TODO: accomodate where clause to put changes to more than one doc.
        
        usrOID     = self.usr['OID']
        data       = kwargs['data']
        _cls       = data['_cls']
        modelClass = getattr(models, _cls)
        #attrNam    = doc['attrNam'] if 'attrNam' in doc_keys else None
        #attr_cls     = doc['attr_cls'] if attrNam else None
        #attrEid    = doc['attrEid'] if attrNam else None
        #attrVal    = doc['attrVal'] if attrNam else None
        collNam    = modelClass.meta['collection']
        coll       = db[collNam]
        
        response   = {}
        docs       = []
        status     = 200
        
        where      = data['where']
        patch      = data['patch']
        eId        = data['eId'] if 'eId' in data else None
        
        # if element eId was passed, expect to put/patch change to one element in a ListField
        if eId and len(patch) == 1:
            elem    = patch.popitem()
            attrNam = elem[0]

            # enhance to support putting/updating multiple list elements
            attrVal = elem[1][0]
            
            resp    = preSave(attrVal, self.usr)
            if not resp['status'] == 200:
                return {'response': resp, 'status': 400}
            
            attrVal = resp['response']['doc']
            # http://docs.mongodb.org/manual/applications/update/
            # patch update in tmp collection
            attrEl = attrNam + '.$'
            doc = collTmp.find_and_modify(
                query = where,
                update = { "$set": { attrEl: attrVal }},
                new = True
            )
            response['collection'] = collNamTmp
            response['total_invalid'] = 0
            response['id'] = id.__str__()
    
            # remove this, not needed
            response['doc'] = doc

            return {'response': response, 'status': 200}
        else:
            # validate patch
            # init modelClass for this doc
            patch_errors = validate_partial(modelClass, patch)
            if patch_errors:
                response['errors'] = patch_errors['errors']
                response['total_errors'] = patch_errors['count']
                status = 500
    
                return prep_response(response, status = status)
    
            # logit update
            patch = logit(self.usr, patch)
                    
            # patch update in tmp collection
            doc = collTmp.find_and_modify(
                query = where,
                update = {"$set": patch},
                new = True
            )

        # init model instance
        model      = modelClass(**doc)
        
        response['total_invalid'] = 0
        response['id'] = id.__str__()

        return {'response': response, 'status': status}
