# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
from app import app

class Lnk(object):
    def __init__(self, g):
        self.g   = g
        self.usr = g['usr']
        self.db  = g['db']
        #self.es  = g['es']
    def put(self, _cls, query, update, lnkTo=None):
        db           = self.db
        mgodb        = db.connection[db.app.config['MONGODB_DB']]
        _clss        = self.g['_clss']
        response     = {}
        status       = 200
        doc_errors = []

        usrOID       = self.usr['OID']

        # get par class that we will create a lnk/path to
        lnkTo['Cls']     = getattr(mdls, lnkTo['_cls'])
        lnkTo['collNam'] = _clss[lnkTo['_cls']]['collNam']
        lnkTo['coll']    = mgodb[lnkTo['collNam']]

        # get par doc
        lnkTo['data']    = lnkTo['coll'].find_one({'slug': lnkTo['slug']})
        lnkTo['doc']     = lnkTo['Cls'](**lnkTo['data'])

        # get par class that we will create a lnk/path
        chldCls     = getattr(mdls, _cls)
        chldCollNam = _clss[_cls]['collNam']
        chldColl    = mgodb[chldCollNam]

        # find and lock the target (child) doc that will be updated
        # query should find doc with pars/pths we will be $push(ing) data to
        targetDoc  = chldColl.find_and_modify(
              query = query,
              update = {'$set': {'locked': True}},
              new = True
          )
        target = chldCls(**targetDoc)

        # get role details
        # get par class that we will create a lnk/path
        lnkRoleCls     = getattr(mdls, 'LnkRole')
        lnkRoleCollNam = _clss['LnkRole']['collNam']
        lnkRoleColl    = mgodb[lnkRoleCollNam]

        lnkRoleDat = lnkRoleColl.find_one({'slug': lnkTo['role']})
        lnkRole    = lnkRoleCls(**lnkRoleDat)


        # init $push actions for pars and pths
        flds = {}

        # init Par to be pushed to pars
        par      = mdls.Par()
        par.cls  = lnkTo['_cls']
        par.slug = lnkTo['slug']
        par.role = lnkRole.par # role is from the perspective of target/parent
        par.mask = lnkRole.mask

        flds['pars'] = par.cleanData()
        pths = []

        # init Pth to be pushed to pths
        pth      = {}
        pth['cls']  = lnkTo['_cls']
        pth['slug'] = lnkTo['slug']
        pth['role'] = lnkRole.chld # role is from the perspective of subject/child
        pth['uris'] = [lnkTo['_cls'] + '.' + lnkTo['slug']]

        pths.append(pth)

        if lnkRole.slug == 'unit-area':
            pass
        # gather par pths
        # filter to avoid dups!
        if lnkTo['doc'].pths:
            for pthItem in lnkTo['doc']['pths']:
                pthItem['uris'] = list(pthItem['uris'])
                pthItem['uris'].append(lnkTo['_cls'] + '.' + lnkTo['slug'])
                pths.append(dict(pthItem))
            pass


        errors      = {}
        doc_info    = {}
        patchActions = {}
        patchActions['$push'] = flds

        if doc_errors:
            response['errors']        = doc_errors
            status                    = 500
        else:

            update   = {'$push': {'fldUpdates': flds}}
            # $push pars
            doc = chldColl.find_and_modify(
                query = query,
                update = patchActions,
                new = True
            )

            flds = {}
            flds['pths'] = pths
            for pth in pths:
                # $push pths for each pth
                patchActions['$push'] = {'pths': pth}
                doc = chldColl.find_and_modify(
                    query = query,
                    update = patchActions,
                    new = True
                )

            # need to include fldUpdate to unlock targetDoc
            if not '$unset' in patchActions:
                patchActions['$unset'] = {}

            doc  = chldColl.find_and_modify(
                  query = query,
                  update = {'$set': {'locked': True}},
                  new = True
              )

            patchActions['$unset']['locked'] = True
            response['_id'] = doc['_id']
            response['OID'] = doc['_id'].__str__()
            response['doc'] = doc

        return {'response': response, 'status': status}
