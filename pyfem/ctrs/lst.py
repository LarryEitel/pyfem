# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
import ctrs
from mdls import *

class Lst(object):
    def cmd(self, cmd):
        # example: 'cnts|q:emails.address:bill@ms.com|fields:cNam,_id:0|sorts:cNam-1|vflds:1|skip:0|limit:1'
        g = app.g
        debug = g['logger'].debug
        get    = ctrs.get.Get().get
        fldClss = g['fldClss']

        debug(u'\n' + (u'_'*50) + u'\n' + cmd + u'\n' + (u'_'*50))
        params = cmd.split('|')
        collNam = params.pop(0)

        get_one = collNam[-2:] == ':1'
        collNam = collNam[:-2] if get_one else collNam

        data = dict(collNam=collNam)
        for _param in params:
            param = _param[0:_param.index(':')]
            _param = _param[_param.index(':')+1:]
            if param == 'q':
                query = {}
                _paramParts = _param.split(',')
                for _paramPart in _paramParts:
                    _paramPartSplit = _paramPart.split(':')
                    query[_paramPartSplit[0]] = _paramPartSplit[1]
                data['query'] = query
            elif param == 'fields':
                data['fields'] = _param
            elif param == 'sorts':
                data['sorts'] = _param
            elif param == 'vflds':
                data['vflds'] = True
            elif param == 'skip':
                data['skip'] = _param
            elif param == 'limit':
                data['limit'] = _param

        if get_one:
            data['skip'] = 0
            data['limit'] = 1

        docs = get(**data)
        return docs


    def lst_one(self,
            collNam,       # ie cnts
            query=None,    # ie {'slug':'ni'}
            fields=None,   # ie fNam, lNam,_id:0
            sorts=None,    # ie cNam-1 ## cNam descending
            limit=0,
            vflds=False    # ie vflds:1 ## include virtual fields like vNam
            ):
        return self.get(**dict(collNam=collNam, query=query, fields=fields, sorts=sorts, vflds=vflds, limit=1))

    def lst(self, collNam, query=None, fields=None, sorts=None, skip=0, limit=0, vflds=False):
        '''
            Nam,       # ie cnts
            query=None,    # ie {'slug':'ni'}
            fields=None,   # ie fNam, lNam,_id:0
            sorts=None,    # ie cNam-1 ## cNam descending
            skip=0,
            limit=0,
            vflds=False    # ie vflds:1 ## include virtual fields like vNam
            '''
        debug    = app.g['logger'].debug
        me       = app.me
        g        = app.g
        D        = ctrs.d.D
        pymongo  = app.pymongo

        coll     = pymongo[collNam]


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

            # make sure _c included
            flds['_c'] = 1
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

        if not vflds:
            if sorts:
                cursor = coll.find(query, fields = fields, skip = int(skip), limit = int(limit)).sort(sorts)
            else:
                cursor = coll.find(query, fields = fields, skip = int(skip), limit = int(limit))
        else:
            # need all field for virtual functions, filter fields later if requested
            if sorts:
                cursor = coll.find(query, skip = int(skip), limit = int(limit)).sort(sorts)
            else:
                cursor = coll.find(query, skip = int(skip), limit = int(limit))


        docs = []
        for doc in cursor:
            # handle any virtual fields
            if vflds:
                docCls = getattr(ctrs.d, doc['_c'])
                docFlds = {}
                for vfld in [vfld for vfld in dir(docCls)
                             if vfld[0] == 'v'
                             and hasattr(getattr(docCls, vfld), '__call__')]:


                    docFlds[vfld] = getattr(docCls, vfld)(**doc)
                    doc[vfld] = getattr(docCls, vfld)(**doc)

                    # filter fields here cause needed fields for virtual functions
                    if fields:
                        _doc = {}
                        for fld in [k for k,v in fields.iteritems() if v]:
                            _doc[fld] = doc[fld]
                        doc = _doc

                for k, v in docFlds.iteritems():
                    doc[k] = v
            docs.append(doc)

        if int(limit) == 1 and not skip and docs:
            return docs[0]

        return docs