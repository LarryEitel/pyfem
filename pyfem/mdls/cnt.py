import datetime

from app import app
import mdls
from mdls import Mixin, Email, Note, D
from mdls.myfields import MyStringField
import helpers

import utils.name

class Cnt(D, Mixin):
    code = app.me.StringField()

    # need this.
    meta = {'allow_inheritance': True,
            'indexes': [
                {'fields':['slug'], 'unique': True},
                {'fields':['sId'], 'unique': True},
                {'fields':['pars.cls', 'pars.slug']},
                {'fields':['pths.uris']},
                {'fields':['-mOn']}
                ]
            }
    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        # needed this otherwise it would use d for collection name
        self._meta['collection'] = 'cnts'
        if type(errors) == list:
            self._data['myErrors'] = errors
        else:

            # we want to generate a slug and make sure whatever slug may have been
            # given, if any, will be unique
            slugDefault = self.slug or self.dNam
            self.slug = self.generate_slug(slugDefault)


            # turning off validation cause we do that in recurseValidateAndVOnUpSert
            kwargs['validate'] = False

            # this will return error if duplicate entries are attempted
            try:
                super(Cnt, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e


class Cmp(Cnt):
    symbol = app.me.StringField()
    cNam   = MyStringField(required=True)

    meta = {
        'indexes': [{'fields':['cNam'], 'sparse': True}]
        }

class Prs(Cnt):
    # namePrefix
    prefix    = app.me.StringField()

    # givenName
    fNam      = MyStringField(required=True)

    # additionalName
    fNam2     = app.me.StringField()

    # givenName
    lNam      = app.me.StringField()
    lNam2     = app.me.StringField()

    # nameSuffix
    suffix    = app.me.StringField()
    gen       = app.me.StringField()
    rBy       = app.me.ObjectIdField()

    meta = {
        'indexes': [{'fields':['prefix', 'fNam', 'fNam2', 'lNam', 'lNam2', 'suffix']}]
        }

        # unsuccessfully tried to use unique index to prevent dup on prim and typ+email, resorted to code hack
        #{'fields':['emails.typ', 'emails.address'], 'unique': True}
        #{'fields':['emails.address'], 'unique': True},
        #{'fields':['emails.prim'], 'unique': True}

        # 'indexes': [{'fields':['slug'], 'unique': True}]
        # 'indexes': [{'fields':['slug'], 'unique': True}, {'fields':['emails.prim'], 'unique': True}]
        # 'indexes': [{'fields':['dNam']}, {'fields':'emails.prim', 'unique': True}]
    @staticmethod
    def staticFullName(prefix='', fNam='', fNam2='', lNam='', lNam2='', suffix=''):
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

    @property
    def fullName(self):
        return self.staticFullName(self.prefix, self.fNam, self.fNam2, self.lNam, self.lNam2, self.suffix)

    @staticmethod
    def staticNam(prefix='', fNam='', fNam2='', lNam='', lNam2='', suffix=''):
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

    @property
    def dNam(self):
        return self.staticNam(self.prefix, self.fNam, self.fNam2, self.lNam, self.lNam2, self.suffix)

    # TODO: Need to make this work
    def get_absolute_url(self):
        return app.url_for('Prs', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # this will return error if duplicate entries are attempted
        # self._meta['collection'] = 'prss'
        try:
            super(Prs, self).save(*args, **kwargs)
        except Exception, e:
            self._data['myErrors'] = e


class Usr(Prs):
    # namePrefix
    uNam    = app.me.StringField(required=True)

    meta = {
        'indexes': [{'fields':['slug'], 'unique': True},
                    {'fields':['sId'], 'unique': True},
                    {'fields':['uNam'], 'unique': True, 'sparse': True},
                    {'fields':['-mOn']}
                    ]
        }

    def get_absolute_url(self):
        return url_for('Usr', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # this will return error if duplicate entries are attempted
        # self._meta['collection'] = 'prss'
        try:
            super(Usr, self).save(*args, **kwargs)
        except Exception, e:
            self._data['myErrors'] = e