import datetime

from app import app
import mdls
from mdls import ED
from mdls.myfields import MyStringField, MyEmailField
from mongoengine_extras.fields import SlugField, AutoSlugField

class Note(ED):
    #address = app.db.EmailField(required= True)
    title = MyStringField(required= True)
    body  = app.db.StringField()

    def __str__(self):
        s = ('[' + str(self.eId) + '] ') if self.eId else ''
        s += (self.typ + ': ') if self.typ else ''
        s += self.title if self.title else ''
        return s
class EDMix(object):
    typ     = MyStringField(required= True)
    w       = app.db.FloatField()
    prim    = app.db.BooleanField()
    note    = app.db.EmbeddedDocumentField(Note)

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

class Par(ED, EDMix):
    cls  = MyStringField(help_text='Parent _cls')
    slug = MyStringField(help_text='Parent slug')
    role = MyStringField(help_text='Child role')
    mask = MyStringField(help_text='Child role mask')

    # when to add?
    shr  = MyStringField(help_text='share mask, 11')
    
    _meta  = {'unique_with': ['cls', 'slug', 'role']}

class Pth(ED, EDMix):
    cls  = MyStringField(help_text='Parent _cls')
    slug = MyStringField(help_text='Parent slug')
    role = MyStringField(help_text='Child role')
    
    
    pth  = MyStringField(help_text='Cmp.ni.admin.11')
    uris = app.db.ListField(app.db.StringField())

    _meta  = {'unique_with': ['cls', 'slug', 'role']}


class Tel(ED, EDMix):
    text = MyStringField(required= True)

class Email(ED, EDMix):
    address = MyEmailField(required= True)

    def __repr__(self):
        s = ('[' + str(self.eId) + '] ') if self.eId else ''
        s += (self.typ + ': ') if self.typ else ''
        s += self.address if self.address else ''
        return s

    _meta = {'unique_with': ['address']}

    # @staticmethod
    # def vOnUpSert(d):
    #     errors = []
    #     dNam = (d['typ'] + ': ') if 'typ' in d and d['typ'] else ''
    #     dNam += d['address'].lower() if 'address' in d and d['address'] else ''
    #     dNam += ' (Primary)' if 'prim' in d and d['prim'] else ''
    #     d['dNam'] = dNam
    #     dNamS = (d['typ'] + '__') if 'typ' in d and d['typ'] else ''
    #     dNamS += d['address'].lower()
    #     dNamS += '__prim' if 'prim' in d and d['prim'] else ''
    #     d['dNamS'] = dNamS
    #     return {'doc_dict': d, 'errors': errors}

    def save(self, *args, **kwargs):
        super(Email, self).save(*args, **kwargs)


class Mixin(object):
    pars   = app.db.ListField(app.db.EmbeddedDocumentField(Par))
    pths   = app.db.ListField(app.db.EmbeddedDocumentField(Pth))
    # chlds  = app.db.ListField(app.db.EmbeddedDocumentField(Pth))
    emails = app.db.ListField(app.db.EmbeddedDocumentField(Email))
    notes  = app.db.ListField(app.db.EmbeddedDocumentField(Note))
    slug   = app.db.StringField()

    sId    = app.db.SequenceField()

    oBy    = app.db.ObjectIdField()
    oOn    = app.db.DateTimeField()
    cBy    = app.db.ObjectIdField()
    mBy    = app.db.ObjectIdField()
    mOn    = app.db.DateTimeField()
    dOn    = app.db.DateTimeField()
    dBy    = app.db.ObjectIdField()
