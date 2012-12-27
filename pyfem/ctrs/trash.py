# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
import ctrs
from mdls import *

class Trash(object):
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


    def trash_one(self, collNam, query=None, cascade=False):
        debug    = app.g['logger'].debug
        me       = app.me
        g        = app.g
        D        = ctrs.d.D
        pymongo  = app.pymongo

        response   = {}
        status     = 200

        coll     = pymongo[collNam]

        # find and set trash = true
        target  = coll.find_and_modify(
              query = query,
              update = {'$set': {'trash': True}},
              new = True
            )
        if not target:
            return {'response': dict(errors="Failed to trash.", status=500)}

        # find and immediate children
        chlds = []
        for chld in coll.find({'pars.cls': target['_c'], 'pars.slug': target['slug']}, {'_c':1, 'slug':1, '_id':1}):
            chlds.append(chld)

        # trash par/parent links to trashed doc
        for doc in chlds:
            doc  = coll.find_and_modify(
                  query = {'_id': doc['_id'], 'pars.cls': target['_c'], 'pars.slug': target['slug']},
                  update = {'$set': {'pars.$.trash': True}},
                  new = True
                )
            if not doc:
                return {'response': dict(errors="Failed to trash parent lnk.", status=500)}


        # delete all lnks that reference target doc in pths
        # what about other collections?
        targetUri = target['_c'] + '.' + target['slug']
        for descendent in coll.find({'pths.uris': targetUri}, {'pths':1, '_id': 1}):
            # cruise through pths and trash any with ref's to target uri
            pths = descendent['pths']
            for i, lnk in enumerate(pths):
                if targetUri in lnk['uris']:
                    pths[i]['trash'] = True
                pass

            doc = coll.find_and_modify(
                query = {'_id': descendent['_id']},
                update = {'$set': {'pths': pths}},
                new = True
            )
            if not doc:
                return {'response': dict(errors="Failed to trash pth.", status=500)}


        response['_id'] = target['_id']
        response['OID'] = target['_id'].__str__()
        response['doc'] = target

        return {'response': response, 'status': status}


    def trash(self, collNam, query=None, cascade=False, limit=0):
        '''
            Nam,       # ie cnts
            query=None,    # ie {'slug':'ni'}
            cascade,
            limit=0,
            '''
        debug    = app.g['logger'].debug
        me       = app.me
        g        = app.g
        D        = ctrs.d.D
        pymongo  = app.pymongo

        coll     = pymongo[collNam]

        resps = []
        for doc in coll.find(query = query):
            resp = self.trash_one(collNam, query=dict(_id=doc['_id']), cascade=cascade)
            resps.append(resp)


        if int(limit) == 1 and resps:
            return resps[0]

        return resps