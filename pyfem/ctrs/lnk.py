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
    def add(self, chld_, par_, role_):
        db           = self.db
        mgodb        = db.connection[db.app.config['MONGODB_DB']]
        _clss        = self.g['_clss']
        response     = {}
        status       = 200
        doc_errors = []
        usrOID       = self.usr['OID']

        query = {'slug': chld_['slug']}

        # get par class that we will create a lnk/path to
        parCls     = getattr(mdls, par_['_cls'])
        parCollNam = _clss[par_['_cls']]['collNam']
        parColl    = mgodb[parCollNam]

        # get par_/par doc
        par    = parColl.find_one({'slug': par_['slug']})

        # get par_/par class that we will create a lnk/path
        chldCls     = getattr(mdls, chld_['_cls'])
        chldCollNam = _clss[chld_['_cls']]['collNam']
        chldColl    = mgodb[chldCollNam]

        # find and lock the child doc that will be updated
        ### RACE: Handle if already locked, retry
        doc  = chldColl.find_and_modify(
              query = query,
              update = {'$set': {'locked': True}},
              new = True
          )

        # get role details
        roleCollNam = _clss['LnkRole']['collNam']
        roleColl    = mgodb[roleCollNam]

        role = roleColl.find_one({'slug': role_})

        # init $push actions for pars and pths
        flds = {}

        # init parLnk to be pushed to chld.pars
        parLnk      = dict(cls= par_['_cls'], slug= par_['slug'], role= role['chld'])
        if 'mask' in role and role['mask']: parLnk['mask'] = role['mask']

        pths = []

        # init Pth to be pushed to pths
        parPth      = dict(cls= par_['_cls'], slug= par_['slug'], role= role['par'],
                           uris= [par_['_cls'] + '.' + par_['slug']])

        pths.append(parPth)


        # gather par pths
        # filter to avoid dups!
        if 'pths' in par and par['pths']:
            for pthItem in par['pths']:
                pthItem['uris'] = list(pthItem['uris'])
                pthItem['uris'].append(par_['_cls'] + '.' + par_['slug'])
                pths.append(dict(pthItem))

        errors      = {}
        doc_info    = {}

        # possible errors? from where?
        if doc_errors:
            response['errors']        = doc_errors
            status                    = 500
        else:
            # $push pars
            doc = chldColl.find_and_modify(
                query = query,
                update = {'$push': {'pars': parLnk}},
            )

            # $push pars2
            parPthLnk = dict(pth=parLnk['cls']+'.'+parLnk['slug'], role=parLnk['role'])
            doc = chldColl.find_and_modify(
                query = query,
                update = {'$push': {'pars2': parPthLnk}},
            )

            # push pths
            for pth in pths:
                # $push pths for each pth
                doc = chldColl.find_and_modify(
                    query = query,
                    update = {'$push': {'pths': pth}},
                )


            # need to add lnk to any docs that reference chld as their parent
            # add this pth to their pths
            # if son is lnk'd to dad, son has a par.lnk to dad and pth.lnk to dad
            # if dad in lnk'd to HIS dad, then son will gain a lnk to his dad's dad in son's pths.

            if role['slug'] == 'office':
                pass

            # $push pars
            # need to add to parPth.uris
            parPth['uris'].append(chld_['_cls'] + '.' + chld_['slug'])
            for _id in chldColl.find({'pths.uris': chld_['_cls'] + '.' + chld_['slug']}, {'_id': 1}):
                doc = chldColl.find_and_modify(
                    query = {'_id': _id['_id']},
                    update = {'$push': {'pths': parPth}},
                )

            # unlock
            doc  = chldColl.find_and_modify(
                  query = query,
                  update = {'$unset': {'locked': True}},
                  new = True
              )

            response['_id'] = doc['_id']
            response['OID'] = doc['_id'].__str__()
            response['uri'] = doc['_cls'].split('.')[-1] + '.' + doc['slug']
            response['doc'] = doc

        return {'response': response, 'status': status}

