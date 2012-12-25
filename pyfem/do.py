# -*- coding: utf-8 -*-
import os
import globals
import ctrs

import default_settings
from app import app
from flask.ext.mongoengine import MongoEngine

def _flush_db():
    from mongoengine.connection import _get_db
    me = _get_db()
    #Truncate/wipe the database
    names = [name for name in me.collection_names() \
        if 'system.' not in name]
    [me.drop_collection(name) for name in names]

app.config.from_object('default_settings')

me = MongoEngine()
me.init_app(app)

_flush_db()

g           = globals.load()
g['usr']    = {"OID": "50468de92558713d84b03fd7", "at": (-84.163063, 9.980516)}
g['me']     = app.me
g['logger'] = app.logger

debug = app.logger.debug
post    = ctrs.post.Post(g).post
put     = ctrs.put.Put(g).put

resp = post({'slug': 'lwe', 'lNam': 'Stooge', 'emails': [{'_types': ['Email'], 'prim': True, '_cls': 'Email', 'address': 'bill@ms.com', 'typ': 'work', 'eId': 1}], 'fNam': 'Moe', '_cls': 'Prs'})


resp = put(**{'query': {'slug': 'lwe'}, '_cls': 'Prs', 'update': {'actions': {'$push': {'flds': {'emails': [{'_types': ['Email'], 'typ': 'work', '_cls': 'Email', 'address': 'timothy@ms.com'}]}}}}})

pass