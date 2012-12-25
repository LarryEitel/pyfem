# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import mdls
import globals
from app import app

class Lnk(object):
    def cmd(self, cmd):
        g = app.g
        debug = g['logger'].debug
        fldClss = g['fldClss']

        debug(u'\n' + (u'_'*50) + u'\n' + cmd + u'\n' + (u'_'*50))
        params = cmd.split('|')
        fn = params.pop(0)

        if fn == 'add':
            # example: 'lnkAdd|Cmp.kirmse|Cmp.ni|area-company'
            chld_ = params[0].split('.')
            par_ = params[1].split('.')
            role_ = params[2]
            resp = self.add(**dict(
                chld_=
                    dict(
                        _cls=chld_[0],
                        slug=chld_[1]),
                par_=
                    dict(
                        _cls=par_[0],
                        slug=par_[1]),
                role_=role_))
            assert resp['status'] == 200
            return resp

    def add(self, chld_, par_, role_):
        me           = app.me
        g            = app.g
        pymongo        = app.pymongo
        _clss        = g['_clss']
        response     = {}
        status       = 200
        doc_errors = []
        usrOID       = app.g['usr']['OID']

        query = {'slug': chld_['slug']}

        # get par class that we will create a lnk/path to
        parCls     = getattr(mdls, par_['_cls'])
        parCollNam = _clss[par_['_cls']]['collNam']
        parColl    = pymongo[parCollNam]

        # get par_/par doc
        par    = parColl.find_one({'slug': par_['slug']})

        # get par_/par class that we will create a lnk/path
        chldCls     = getattr(mdls, chld_['_cls'])
        chldCollNam = _clss[chld_['_cls']]['collNam']
        chldColl    = pymongo[chldCollNam]

        # find and lock the child doc that will be updated
        ### RACE: Handle if already locked, retry
        doc  = chldColl.find_and_modify(
              query = query,
              update = {'$set': {'locked': True}},
              new = True
          )
        if not doc:
            return {'response': dict(errors="Failed to lock.", status=500)}

        # get role details
        roleCollNam = _clss['LnkRole']['collNam']
        roleColl    = pymongo[roleCollNam]

        role = roleColl.find_one({'slug': role_})
        if not role:
            return {'response': dict(errors="Failed to find role.", status=500)}

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


        # Gather parent pths to be appended to chldDoc.pths
        if 'pths' in par and par['pths']:
            for pthItem in par['pths']:
                pthItem['uris'] = list(pthItem['uris'])
                pthItem['uris'].append(par_['_cls'] + '.' + par_['slug'])
                pths.append(dict(pthItem))



        # $push pars
        doc = chldColl.find_and_modify(
            query = query,
            update = {'$push': {'pars': parLnk}},
        )
        if not doc:
            return {'response': dict(errors="Failed to push pars.", status=500)}

        # Add pthLnks to chldDoc.pths.
        for pth in pths:
            # $push pths for each pth
            doc = chldColl.find_and_modify(
                query = query,
                update = {'$push': {'pths': pth}},
            )
        if not doc:
            return {'response': dict(errors="Failed to push pths.", status=500)}


        # need to add lnk to any docs that reference chld as their parent
        # add this pth to their pths
        # if son is lnk'd to dad, son has a par.lnk to dad and pth.lnk to dad
        # if dad in lnk'd to HIS dad, then son will gain a lnk to his dad's dad in son's pths.

        if role['slug'] == 'office':
            pass

        # $push pars
        # need to add to parPth.uris
        parPth['uris'].append(chld_['_cls'] + '.' + chld_['slug'])


        # what about other collections?
        for _id in chldColl.find({'pths.uris': chld_['_cls'] + '.' + chld_['slug']}, {'_id': 1}):
            doc = chldColl.find_and_modify(
                query = {'_id': _id['_id']},
                update = {'$push': {'pths': parPth}},
            )
            if not doc:
                return {'response': dict(errors="Failed to push affected pths.", status=500)}

        # unlock chldDoc
        doc  = chldColl.find_and_modify(
              query = query,
              update = {'$unset': {'locked': True}},
              new = True
          )
        if not doc:
            return {'response': dict(errors="Failed to unlock.", status=500)}

        response['_id'] = doc['_id']
        response['OID'] = doc['_id'].__str__()
        response['uri'] = doc['_cls'].split('.')[-1] + '.' + doc['slug']
        response['doc'] = doc

        return {'response': response, 'status': status}

