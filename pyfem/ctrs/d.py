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
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.g = g = globals.load()
        self.db = db = app.db.connection[app.config['MONGODB_DB']]
        _clss = g['_clss']
        colls = {}
        for cls, val in _clss.iteritems():
            colls[cls] = db[val['collNam']]
        self.colls = colls

    @property
    def uri(self):
        return self._cls.split('.')[-1] + '.' + self.slug

    def __repr__(self):
        s = self._cls
        s += ('.' + self.slug) if self.slug else ''
        return s

    def __yaml__(self):
        return self.__repr__()

    def get(self, _cls, query):
        doc = self.db[self.meta['collNam']].find_one(query)
        if doc:
            self._fields = [k for k in doc.iterkeys()]
            for k, v in doc.iteritems():
                setattr(self, k, v)
        return doc

    def in_pths(self):
        uris = {}
        collNams = {}
        for _cls, v in self.g['_clss'].iteritems():
            collNams[v['collNam']] = self.colls[_cls]
        for collNam, coll in collNams.iteritems():
            for doc in coll.find({'pths.uris':self.uri}):
                uri = doc['_cls'].split('.')[-1] + '.' + doc['slug']
                uris[uri] = doc
        return uris


    def ol_dict(self, value={}):
        _cls = self._cls.split('.')[-1]
        if hasattr(self, 'pars') and self.pars:
            value['pars'] = []
            for _par in self.pars:
                value['pars'].append(_par)

        if hasattr(self, 'pths') and self.pths:
            value['pths'] = []
            for _pth in self.pths:
                value['pths'].append(_pth)

        # children
        chlds = []
        collNams = {}
        for _cls, v in self.g['_clss'].iteritems():
            collNams[v['collNam']] = self.colls[_cls]
        level = 0
        for collNam, coll in collNams.iteritems():
            chldsNew = self.getChlds(coll, level)
            if chldsNew:
                chlds += chldsNew
        if chlds:
            value['chlds'] = []
            for line in chlds:
                value['chlds'].append(line['obj'].__yaml__())

        return value

    def to_yaml(self, level):
        yml = '\n'
        # yml += (u'  '*level) + self.__yaml__() + '\n'
        yml += (u'  '*level) + self.__yaml__()
        if hasattr(self, 'pars') and self.pars:
            if level < 1:
                yml += '\n' + (u'  '*(level+1)) + 'pars'
            for _par in self.pars:
                par = Par(**_par)
                # lines.append(dict(level=level+2, obj=par))
                for chld in self.colls[par.cls].find(dict(slug=par.slug)):
                    chld_cls = chld['_cls'].split('.')[-1]
                    doc = getattr(__import__(self.__module__), chld_cls)()
                    doc.get(**dict(_cls=chld_cls, query=dict(slug=chld['slug'])))
                    yml += doc.to_yaml(level+2)

        if level < 1:
            if hasattr(self, 'pths') and self.pths:
                yml += '\n' + (u'  '*(level+1)) + 'pths' + '\n'
                for _pth in self.pths:
                    pth = Pth(**_pth)
                    yml += (u'  '*(level+2)) + pth.__yaml__() + '\n'

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
                yml += (u'  '*(level+1)) + 'Children' + '\n'
                for line in chlds:
                    yml += (u'  '*(line['level'])) + line['obj'].__yaml__() + '\n'

        return yml

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

    def __yaml__(self):
        return self.__repr__()

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

    def __yaml__(self):
        return self.__repr__()

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

def referenced_in_pths(doc):
    debug   = app.logger.debug
    _cls = doc['_cls'].split('.')[-1]
    # did pths get added correctly?
    D = getattr(__import__(__name__), _cls)(**doc)
    in_pths = D.in_pths()

    _dat = {}
    _yml = {}
    debug('\n\n' + D.uri + " referenced in pths")
    for uri, doc in in_pths.iteritems():
        _cls = uri.split('.')[0]
        D = getattr(__import__(__name__), _cls)(**doc)
        _dat[uri] = D.ol_dict()
        yml = D.to_yaml(0)
        _yml[uri] = yml
        debug(yml + '\n')

    return dict(_dat=_dat, _yml=_yml)