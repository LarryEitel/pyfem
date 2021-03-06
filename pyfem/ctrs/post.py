# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import ctrs
import globals
from app import app

class Post(object):
    def cmd(self, cmds):
        g = app.g
        debug = g['logger'].debug
        post    = ctrs.post.Post().post
        fldClss = g['fldClss']

        if not type(cmds) == list: cmds = [cmds]

        resps = []
        errors = 0
        docs = []
        for cmd in cmds:
            debug(u'\n' + (u'_'*50) + u'\n' + cmd + u'\n' + (u'_'*50))
            params = cmd.split('|')

            # example: 'Cmp.ni|slug:new_company,cNam:MS'
            _cls   = params.pop(0)
            data   = dict(_cls=_cls)

            # get flds to set
            doc   = dict([(v.split(':')[0], v.split(':')[1]) for v in params])
            doc['_cls'] = doc['_c'] = _cls
            doc['_types'] = [_cls]
            docs.append(doc)

        resp = post(**{'docs': docs})
        return resp

    def post(self, docs):
        docs = [docs] if type(docs) == dict else docs
        me           = app.me

        response     = {}
        docs_handled = {}
        status       = 200

        usrOID       = app.g['usr']['OID']

        post_errors  = []
        total_errors = 0

        for docData in docs:
            errors      = {}
            doc_info    = {}

            try:
                modelClass = getattr(mdls, docData['_c'])
            except:
                modelClass = getattr(mdls, docData['_cls'])

            doc    = modelClass(**docData)
            doc._c = doc._cls
            resp   = doc.save()
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