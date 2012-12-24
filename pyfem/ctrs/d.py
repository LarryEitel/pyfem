# -*- coding: utf-8 -*-
import os
import re
import datetime
from bson import ObjectId
import globals
from app import app

class D(object):
    _cls = 'D'
    meta = dict(collNam='d')
    def __init__(self):
        self.g = g = globals.load()
        self.db = db = app.db.connection[app.config['MONGODB_DB']]
        _clss = g['_clss']
        colls = {}
        for cls, val in _clss.iteritems():
            colls[cls] = db[val['collNam']]
        self.colls = colls

    def __repr__(self):
        s = self._cls
        s += ('.' + self.slug) if self.slug else ''
        return s

    def get(self, _cls, query):
        doc = self.db[self.meta['collNam']].find_one(query)
        if doc:
            self._fields = [k for k in doc.iterkeys()]
            for k, v in doc.iteritems():
                setattr(self, k, v)
        return doc

    def getOl(self, level=0):
        lines = []
        lines.append(dict(level=level, obj=self))
        return lines

    def getChlds(self, coll, level=0):
        self_cls = self._cls.split('.')[-1]
        chlds = []
        level += 1
        for chld in coll.find({'pars.cls': self_cls, 'pars.slug': self.slug}):
            chld_cls = chld['_cls'].split('.')[-1]
            doc = getattr(__import__(self.__module__), chld_cls)()
            doc.get(**dict(_cls=chld_cls, query=dict(slug=chld['slug'])))

            chlds.append(dict(level=level+1, obj=doc))
            chldNew = doc.getChlds(coll, level)
            chlds += chldNew
        return chlds
    def getOl(self, level=0):
        lines = []
        lines.append(dict(level=level, obj=self))
        if hasattr(self, 'pars') and self.pars:
            if level < 1:
                lines.append(dict(level=level+1, obj='Parents'))
            for _par in self.pars:
                par = Par(**_par)
                # lines.append(dict(level=level+2, obj=par))
                for chld in self.colls[par.cls].find(dict(slug=par.slug)):
                    chld_cls = chld['_cls'].split('.')[-1]
                    doc = getattr(__import__(self.__module__), chld_cls)()
                    doc.get(**dict(_cls=chld_cls, query=dict(slug=chld['slug'])))
                    linesNew = doc.getOl(level+2)
                    lines += linesNew

        if level < 1:
            if hasattr(self, 'pths') and self.pths:
                lines.append(dict(level=level+1, obj='Ancestors'))
                for _pth in self.pths:
                    pth = Pth(**_pth)
                    lines.append(dict(level=level+2, obj=pth))
                    doc = getattr(__import__(self.__module__), par.cls)()
                    doc.get(**dict(_cls=par.cls, query=dict(slug=par.slug)))
                    #lines += tree(doc.getOl(level)

        # children
        chlds = []
        if level < 1:
            collNams = {}
            for _cls, v in self.g['_clss'].iteritems():
                collNams[v['collNam']] = self.colls[_cls]
            for collNam, coll in collNams.iteritems():
                chldsNew = self.getChlds(coll, level)
                if chldsNew:
                    chlds += chldsNew
            if chlds:
                lines.append(dict(level=level+1, obj='Children'))
                lines += chlds

        #if level < 1:
            #chlds = []
            #self_cls = self._cls.split('.')[-1]
            #for chld in self.colls[self_cls].find({'pars.cls': self_cls, 'pars.slug': self.slug}):
                #chld_cls = chld['_cls'].split('.')[-1]
                #doc = getattr(__import__(self.__module__), chld_cls)()
                #doc.get(**dict(_cls=chld_cls, query=dict(slug=chld['slug'])))

                #chlds += doc.getChld(level)

                #chlds.append(dict(level=level+2, obj=doc.__str__()))
            #if chlds:
                #lines.append(dict(level=level+1, obj='Children'))
                #lines += chlds

        return lines
class Pth(object):
    _cls = 'Pth'
    def __init__(self, cls='', slug='', role='', uris=[]):
        self.cls = cls
        self.slug = slug
        self.role = role
        self.uris = uris

    def __repr__(self):
        s = '.'.join([self.cls, self.slug])
        s += '.' + self.role if self.role else ''
        return s

class Par(object):
    _cls = 'Par'
    def __init__(self, cls='', slug='', role='', mask=''):
        self.cls = cls
        self.slug = slug
        self.role = role
        self.mask = mask

    def __repr__(self):
        s = '.'.join([self.cls, self.slug])
        s += '.' + self.role if self.role else ''
        s += '^' + self.mask if self.mask else ''
        return s

class Ol(object):
    def __init__(self):
        self.g = g = globals.load()
        db = app.db.connection[app.config['MONGODB_DB']]
        _clss = g['_clss']
        colls = {}
        for cls, val in _clss.iteritems():
            colls[cls] = db[val['collNam']]
        self.colls = colls

    def show(self, d):
        #print d
        lines = d.getOl()
        for ln in lines:
            print '  '*ln['level'], ln['obj']
        x=0

class Pl(D):
    _cls = 'Pl'
    meta = dict(collNam='pls')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s

class Cnt(D):
    _cls = 'Cnt'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s

class Cmp(Cnt):
    _cls = 'Cmp'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s




class D_(object):
    pass
    #def tree(self, _cls, slug, level):
        #colls = self.colls
        #usrOID       = self.usr['OID']
        #items = []
        #for doc in colls[_cls].find({'pars.cls': _cls, 'pars.slug': slug},
                #dict(pars=1, pths=1, _cls=1, slug=1)):
            #_cls = doc['_cls'].split('.')[-1]

            ## pars
            #items.append(dict(level=level, fld='pars'))

            #par = self.par(doc['pars'], _cls, slug)
            #level += 1
            #items.append(dict(level=level+1, _cls=_cls, role=par['role'], slug=doc['slug']))


            #pths = [dict(cls=item['cls'], role=item['role'], slug=item['slug'], uris=item['uris']) for item in doc['pths']]
            #items.append(dict(level=level+1, pths=pths))
            #items.append(dict(level=level+1, pths=doc['pths']))
            #items += self.tree(_cls, doc['slug'], level)
        #return items


    #def tree2(self, _cls, slug, level):
        #colls = self.colls

        #doc = colls[_cls].find_one({'slug': slug}, dict(pars=1, pths=1, _cls=1, slug=1))
        #print '  '*level, doc['_cls'].split('.')[-1], doc['slug']
        #if 'pars' in doc and doc['pars']:
            #print '  '*(level+1), 'Parents:'
            #for par in doc['pars']:
                #print '  '*(level+2), par
                #_cls = par['cls'].split('.')[-1]
                #self.tree2(_cls, par['slug'], level)

        #if 'pths' in doc and doc['pths']:
            #print '  '*(level+1), 'Paths:'
            #t = []
            #for pth in doc['pths']:
                #print '  '*(level+2), pth
                #_cls = pth['cls'].split('.')[-1]
                #t += self.tree(_cls, pth['slug'], level)

            #for l in t:
                #print '  '*l['level'], '.'.join([str(l[k]) for k,v in l.iteritems()][:-1])

