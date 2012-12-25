# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
from app import app

class Post(object):

    def __init__(self, g):
        #: Doc comment for instance attribute me
        self.g   = g
        self.usr = g['usr']
        self.me  = g['me']
        #self.es  = g['es']

    def post(self, docs):
        docs = [docs] if type(docs) == dict else docs
        me           = self.me

        response     = {}
        docs_handled = {}
        status       = 200

        usrOID       = self.usr['OID']

        post_errors  = []
        total_errors = 0

        for docData in docs:
            errors      = {}
            doc_info    = {}

            modelClass = getattr(mdls, docData['_cls'])

            doc = modelClass(**docData)
            resp = doc.save()
            if 'myErrors' in doc._data:
                error = {'docData': docData, 'errors': doc._data['myErrors']}
                post_errors.append(error)
            else:
                docs_handled[doc.id]   = mdls.helpers.docCleanData(doc._data)

        response['total_inserted'] = len(docs_handled.keys())

        if post_errors:
            response['total_invalid'] = len(post_errors)
            response['errors']        = post_errors
            status                    = 500
        else:
            response['total_invalid'] = 0

        response['docs'] = docs_handled

        return {'response': response, 'status': status}