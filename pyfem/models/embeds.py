import datetime

from app import app
import models
from models import MyEmbedDoc
from models.myfields import MyStringField, MyEmailField
from mongoengine_extras.fields import SlugField, AutoSlugField

class EmbedMixin(object):
    typ     = MyStringField(required= True)
    _eIds   = app.db.DictField()
    dNam    = app.db.StringField()
    dNamS   = app.db.StringField()
    eId     = app.db.IntField()
    w       = app.db.FloatField()
    prim    = app.db.BooleanField()

    def validateList(self, theList):
        errors = {}

        # need to handle unique_with
        if '_meta' in self and 'unique_with' in self._meta:
            unique_with = self._meta['unique_with']

            if len(theList) > 1:
                unique_with_vals = {}

                offendingItem = None
                for i, item in enumerate(theList):
                    unique_with_val = []
                    for unique_with_fld in unique_with:
                        if unique_with_fld in item:
                            unique_with_val.append(item[unique_with_fld])

                    if unique_with_val:
                        unique_with_val_str = '.'.join(unique_with_val)
                        unique_with_vals[unique_with_val_str] = unique_with_vals[unique_with_val_str] + 1 if unique_with_val_str in unique_with_vals else 1
                        if unique_with_vals[unique_with_val_str] > 1:
                            offendingItem = item
                            break

                if offendingItem:
                    errors['+'.join(unique_with)] = '+'.join(unique_with) + ' must be unique.'


        primCount = 0
        for i, item in enumerate(theList):
            if 'prim' in item and item['prim']:
                primCount += 1

        if primCount > 1:
            errors['prim'] = 'Only one permited primary item.'

        return errors

class Tel(MyEmbedDoc, EmbedMixin):
    text = MyStringField(required= True)

class Note(MyEmbedDoc, EmbedMixin):
    #address = app.db.EmailField(required= True)
    title = MyStringField(required= True)
    body  = app.db.StringField()
    tels  = app.db.ListField(app.db.EmbeddedDocumentField(Tel))

    def __str__(self):
        s = ('[' + str(self.eId) + '] ') if self.eId else ''
        s += (self.typ + ': ') if self.typ else ''
        s += self.title if self.title else ''
        return s

    _meta = {'fldsThatUpdt_dNam': ['typ', 'title']}

    @staticmethod
    def vOnUpSert(d):
        errors = []
        dNam = (d['typ'] + ': ') if 'typ' in d and d['typ'] else ''
        dNam += d['title'] if 'title' in d and d['title'] else ''
        d['dNam'] = dNam
        dNamS = (d['typ'] + '__') if 'typ' in d and d['typ'] else ''
        dNamS += d['title'].lower().replace(' ', '_')
        d['dNamS'] = dNamS
        return {'doc_dict': d, 'errors': errors}

class Email(MyEmbedDoc, EmbedMixin):
    address = MyEmailField(required= True)
    notes   = app.db.ListField(app.db.EmbeddedDocumentField(Note))

    def __repr__(self):
        s = ('[' + str(self.eId) + '] ') if self.eId else ''
        s += (self.typ + ': ') if self.typ else ''
        s += self.address if self.address else ''
        return s



    _meta = {'fldsThatUpdt_dNam': ['typ', 'address'],
             'unique_with': ['typ', 'address']}

    @staticmethod
    def vOnUpSert(d):
        errors = []
        dNam = (d['typ'] + ': ') if 'typ' in d and d['typ'] else ''
        dNam += d['address'].lower() if 'address' in d and d['address'] else ''
        dNam += ' (Primary)' if 'prim' in d and d['prim'] else ''
        d['dNam'] = dNam
        dNamS = (d['typ'] + '__') if 'typ' in d and d['typ'] else ''
        dNamS += d['address'].lower()
        dNamS += '__prim' if 'prim' in d and d['prim'] else ''
        d['dNamS'] = dNamS
        return {'doc_dict': d, 'errors': errors}

    def save(self, *args, **kwargs):
        super(Email, self).save(*args, **kwargs)


class Mixin(object):
    _eIds  = app.db.DictField()
    emails = app.db.ListField(app.db.EmbeddedDocumentField(Email))
    notes  = app.db.ListField(app.db.EmbeddedDocumentField(Note))
    dNam   = app.db.StringField()
    dNamS  = app.db.StringField()
    slug   = app.db.StringField()

    sId    = app.db.SequenceField()

    oBy    = app.db.ObjectIdField()
    oOn    = app.db.DateTimeField()
    cBy    = app.db.ObjectIdField()
    cOn    = app.db.DateTimeField()
    mBy    = app.db.ObjectIdField()
    mOn    = app.db.DateTimeField()
    dOn    = app.db.DateTimeField()
    dBy    = app.db.ObjectIdField()


    # not used, hacking
    def validateList(self, theList):
        pass