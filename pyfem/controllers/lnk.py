# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import models
import globals
from app import app

class Lnk(object):

    def __init__(self, g):
        #: Doc comment for instance attribute db
        self.g   = g
        self.usr = g['usr']
        self.db  = g['db']
        #self.es  = g['es']

    def post(self, src, dst, lnkRel):
        db           = self.db

        response     = {}
        docs         = {}
        status       = 200

        usrOID       = self.usr['OID']

        post_errors  = []
        total_errors = 0

        # init src & dst objects
        src_cls  = src.split('.')[0]
        srcClass = getattr(models, src_cls)
        srcSlug  = src.split('.')[1]
        srcObj   = srcClass.objects.get(slug=srcSlug)

        dst_cls  = dst.split('.')[0]
        dstClass = getattr(models, dst_cls)
        dstSlug  = dst.split('.')[1]
        dstObj   = dstClass.objects.get(slug=dstSlug)

        srcLnkRel = lnkRel.split('.')[0]
        dstLnkRel = lnkRel.split('.')[1]

        # src/source is always the FROM link
        # ie, if link from daughter to father, src=daughter doc, pth will be inserted in daughter's pars attribute
        srcLnkClass = getattr(models, 'Lnk')
        srcLnk = srcLnkClass(**{'doc_cls': dst_cls, 'slug': dstSlug, 'lnkTypDNamS': dstLnkRel, 'dDNam': dstObj.dNam})


        srcPthClass = getattr(models, 'Pth')
        srcPth      = srcPthClass()
        srcPth.lnks = [srcLnk.to_mongo()]

        srcClass.objects(slug=srcSlug).update_one(push__pars=srcPth.to_mongo())


        # dst/source is always the from in the link
        dstLnkClass = getattr(models, 'Lnk')
        dstLnk      = dstLnkClass(**{'doc_cls': src_cls, 'slug': srcSlug, 'lnkTypDNamS': srcLnkRel, 'dDNam': srcObj.dNam})
        dstPthClass = getattr(models, 'Pth')
        dstPth      = dstPthClass()
        dstPth.lnks = [dstLnk.to_mongo()]

        dstClass.objects(slug=dstSlug).update_one(push__chlds=dstPth.to_mongo())

        errors      = {}
        doc_info    = {}


        response['total_inserted'] = len(docs.keys())

        if post_errors:
            response['total_invalid'] = len(post_errors)
            response['errors']        = post_errors
            status                    = 500
        else:
            response['total_invalid'] = 0

        response['docs'] = docs

        return {'response': response, 'status': status}