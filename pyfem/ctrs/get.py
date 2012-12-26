# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
import ctrs
from mdls import *

class Get(object):
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
            flds   = dict([(v.split(':')[0], v.split(':')[1]) for v in params])

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
            assert resp['status'] == 200
            return resp

    def get(self, collNam, query=None, fields=None, sorts=None, skip=0, limit=0, vflds=False):
        debug    = app.g['logger'].debug
        me       = app.me
        g        = app.g
        D        = ctrs.d.D
        pymongo  = app.pymongo

        coll       = pymongo[collNam]


        if fields:
            # mongo wants fields like: { item: 1, qty: 1, _id:0 }
            fields = fields.replace(' ', '').split(',')
            flds = {}
            for fld in fields:
                # if fld:0 then strip it off and set to exclude from returned fields
                if ':0' in fld:
                    flds[fld[:-2]] = 0
                else:
                    flds[fld] = 1
            fields = flds

        if sorts:
            # mongo wants sorts like: [("fld1", <order>), ("fld2", <order>)]
            sorts = sorts.replace(' ', '').split(',')
            flds = []
            for fld in sorts:
                # if fld:0 then strip it off and set to exclude from returned fields
                if fld[-2:] == '-1':
                    flds.append((fld[:-2], -1))
                else:
                    flds.append((fld, 1))
            sorts = flds

        if sorts:
            cursor = coll.find(query, fields = fields, skip = int(skip), limit = int(limit)).sort(sorts)
        else:
            cursor = coll.find(query, fields = fields, skip = int(skip), limit = int(limit))

        docs = []
        for doc in cursor:
            # handle any virtual fields
            if vflds:
                docCls = getattr(ctrs.d, doc['_c'])
                for vfld in [vfld for vfld in dir(docCls)
                             if vfld[0] == 'v'
                             and hasattr(getattr(docCls, vfld), '__call__')]:
                    doc[vfld] = getattr(docCls, vfld)(**doc)
            docs.append(doc)

        return docs