import datetime

from app import app
import models
from models import Mixin, Email, Note, MyDoc
from models.myfields import MyStringField
import helpers

class Cnt(MyDoc, Mixin):
    code = app.db.StringField()

    _meta = {
        'collection': 'cnts',
        'allow_inheritance': True
        }

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'cnts'
        if type(errors) == list:
            self._data['myErrors'] = errors
        else:
            # turning off validation cause we do that in recurseValidateAndVOnUpSert
            kwargs['validate'] = False

            # this will return error if duplicate entries are attempted
            try:
                # override collection for this class
                # self.__class__.objects._collection_obj = self.__class__.objects._collection.database[self._meta['collection']]
                super(Cnt, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e


class Cmp(Cnt):
    symbol = app.db.StringField()


class Prs(Cnt):
    # namePrefix
    prefix    = app.db.StringField()

    # givenName
    fNam      = MyStringField(required=True)

    # additionalName
    fNam2     = app.db.StringField()

    # givenName
    lNam      = app.db.StringField()
    lNam2     = app.db.StringField()

    # nameSuffix
    suffix    = app.db.StringField()
    gen       = app.db.StringField()
    rBy       = app.db.ObjectIdField()


    meta = {
        'allow_inheritance': True,
        'fldsThatUpdt_dNam': ['prefix', 'fNam', 'fNam2', 'lNam', 'lNam2', 'suffix'],
        'indexes': [{'fields':['slug'], 'unique': True},
                    {'fields':['sId'], 'unique': True}
                    ]
        }

        # unsuccessfully tried to use unique index to prevent dup on prim and typ+email, resorted to code hack
        #{'fields':['emails.typ', 'emails.address'], 'unique': True}
        #{'fields':['emails.prim'], 'unique': True}

        # 'indexes': [{'fields':['slug'], 'unique': True}]
        # 'indexes': [{'fields':['slug'], 'unique': True}, {'fields':['emails.prim'], 'unique': True}]
        # 'indexes': [{'fields':['dNam']}, {'fields':'emails.prim', 'unique': True}]

    @staticmethod
    def vOnUpSert(d):
        errors = []
        d['dNam'] = d['fNam'] + ' ' + d['lNam']
        if not 'dNamS' in d or not d['dNamS']:
            d['dNamS'] = d['dNam'].lower().replace(' ', '_')
        if not 'slug' in d or not d['slug']:
            d['slug'] = d['dNamS']
        return {'doc_dict': d, 'errors': errors}


    def save(self, *args, **kwargs):
        # this will return error if duplicate entries are attempted
        # self._meta['collection'] = 'prss'
        try:
            super(Prs, self).save(*args, **kwargs)
        except Exception, e:
            self._data['myErrors'] = e