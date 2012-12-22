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
        docs         = {}
        status       = 200

        usrOID       = self.usr['OID']

        op_errors    = []
        total_errors = 0

        # get par class that we will create a lnk/path to
        parCls     = getattr(mdls, lnkTo['_cls'])
        parCollNam = _clss[lnkTo['_cls']]['collNam']
        parColl    = mgodb[parCollNam]

        # get par doc
        parDat    = parColl.find_one(query = {'slug': lnkTo['slug']})
        par       = parCls(**parDat)

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

        lnkRoleDat = lnkRoleColl.find_one(query = {'slug': lnkTo['role']})
        lnkRole    = lnkRoleCls(**lnkRoleDat)


        errors      = {}
        doc_info    = {}


        response['total_inserted'] = len(docs.keys())

        if op_errors:
            response['total_invalid'] = len(op_errors)
            response['errors']        = op_errors
            status                    = 500
        else:
            response['total_invalid'] = 0

        response['docs'] = docs

        return {'response': response, 'status': status}