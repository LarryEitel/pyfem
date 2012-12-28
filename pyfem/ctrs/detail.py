# -*- coding: utf-8 -*-
import os
import datetime
import mdls
import globals
import ctrs

class Detail(object):
    def cmd(self, cmd):
        # example: 'cnts|q:emails.address:bill@ms.com|fields:cNam,_id:0|sorts:cNam-1|vflds:1|skip:0|limit:1'
        g = app.g

    def detail(self, doc):
        debug    = app.g['logger'].debug
        g        = app.g
        D        = ctrs.d.D
        pymongo  = app.pymongo

        coll     = pymongo[collNam]

        return doc