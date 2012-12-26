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
        self.pymongo = pymongo = app.pymongo
        _clss = g['_clss']
        colls = {}
        for cls, val in _clss.iteritems():
            colls[cls] = pymongo[val['collNam']]
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
        doc = self.pymongo[self.meta['collNam']].find_one(query)
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
        debug = app.logger.debug
        yml = '\n'
        yml += (u'  '*level) + self.__yaml__()
        if hasattr(self, 'pars') and self.pars:
            if level < 1:
                yml += '\n' + (u'  '*(level+1)) + 'pars'
                level += 1

            for _par in self.pars:
                par = Par(**_par)
                yml += par.to_yaml(level+1)
                #for chld in self.colls[par.cls].find(dict(slug=par.slug)):
                    #chld_cls = chld['_cls'].split('.')[-1]
                    #doc = getattr(__import__(self.__module__), chld_cls)()
                    #doc.get(**dict(_cls=chld_cls, query=dict(slug=chld['slug'])))
                    ##debug('About to recurse')
                    #yml += doc.to_yaml(level+1)
                    ##if level < 2:
                        ###yml += par.to_yaml(level+1)
                        ##yml += doc.to_yaml(level+1)
                    ##else:
                        ##yml += doc.to_yaml(level+1)
                    ##debug('Return from recurse:\n' + yml)

        if level < 2:
            level -= 1 # hackage!
            if hasattr(self, 'pths') and self.pths:
                yml += '\n' + (u'  '*(level+1)) + 'pths' + '\n'
                for _pth in self.pths:
                    pth = Pth(**_pth)
                    yml += (u'  '*(level+2)) + pth.__yaml__() + '\n'

        # children
        chlds = []
        if level < 2:
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
    _cls = _c = 'Pth'
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
        return self.__repr__() + ': [' + (','.join(self.uris)) + ']'
class Par(object):
    _cls = _c = 'Par'
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

    def to_yaml(self, level):
        return '\n' + (u'  '*(level)) + self.__yaml__()

    def __yaml__(self):
        return self.__repr__()
class Ol(object):
    def __init__(self):
        self.g = g = globals.load()
        pymongo = app.pymongo.connection[app.config['MONGODB_DB']]
        _clss = g['_clss']
        colls = {}
        for cls, val in _clss.iteritems():
            colls[cls] = pymongo[val['collNam']]
        self.colls = colls

    def show(self, d):
        #print d
        lines = d.getOl()
        for ln in lines:
            print '  '*ln['level'], ln['obj']
        x=0
class Pl(D):
    _cls = _c = 'Pl'
    meta = dict(collNam='pls')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s
class Cnt(D):
    _cls = _c = 'Cnt'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s

class Cmp(Cnt):
    _cls = _c = 'Cmp'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s

    @staticmethod
    def vNam(cNam, **kwargs):
        s = ''
        s += cNam
        return s

class Prs(Cnt):
    _cls = _c = 'Prs'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])

        return s
    @staticmethod
    def vFullName(prefix='', fNam='', fNam2='', lNam='', lNam2='', suffix='', **kwargs):
        '''Mr Bill Wayne Smith Sr'''
        s = ''
        fNamS = ''
        fNamS += prefix + ' ' if prefix else ''
        fNamS += fNam + ' ' if fNam else ''
        fNamS += fNam2 + ' ' if fNam2 else ''
        fNamS = fNamS[:-1] if fNamS else ''

        lNamS = ''
        lNamS += lNam + ' ' if lNam else ''
        lNamS += lNam2 + ' ' if lNam2 else ''
        lNamS += suffix + ' ' if suffix else ''
        lNamS = lNamS[:-1] if lNamS else ''

        return fNamS + (' ' + lNamS if lNamS else '')

    @staticmethod
    def vNam(prefix='', fNam='', fNam2='', lNam='', lNam2='', suffix='', **kwargs):
        s = ''
        fNamS = ''
        fNamS += prefix + ' ' if prefix else ''
        fNamS += fNam + ' ' if fNam else ''
        fNamS += fNam2 + ' ' if fNam2 else ''
        fNamS = fNamS[:-1] if fNamS else ''

        lNamS = ''
        lNamS += lNam + ' ' if lNam else ''
        lNamS += lNam2 + ' ' if lNam2 else ''
        lNamS += suffix + ' ' if suffix else ''
        lNamS = lNamS[:-1] if lNamS else ''

        if lNamS:
            s += lNamS
            if fNamS:
                s += ', ' + fNamS
        elif fNamS:
            s += fNamS
        return s


class Usr(Prs):
    _cls = _c = 'Usr'
    meta = dict(collNam='cnts')

    def __repr__(self):
        _cls = self._cls.split('.')[-1]
        s = '.'.join([_cls, self.slug])
        return s


def to_yaml(doc):
    debug   = app.logger.debug
    _cls = doc['_cls'].split('.')[-1]
    D = getattr(__import__(__name__), _cls)(**doc)
    yml = D.to_yaml(0)
    debug(yml + '\n')
    return yml


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

class DS(object):
    @staticmethod
    def listDocs(docs):
        _list = []
        for doc in docs:
            item = []
            item.append('.'.join([doc['_c'], doc['slug']]))
            docCls = getattr(__import__(__name__), doc['_c'])
            if getattr(docCls, 'vNam'):
                item.append(getattr(docCls, 'vNam')(**doc))
            else:
                item.append(doc.__str__())

            _list.append(item)
        for item in _list:
            s = ', '.join(item)
            app.logger.debug(s)
            print s