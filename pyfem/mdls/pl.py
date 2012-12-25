import datetime

from app import app
import mdls
from mdls import Mixin, Email, Note, D
from mdls.myfields import MyStringField
import helpers

import utils.name

class Pl(D, Mixin):
    code = app.me.StringField()
    city = MyStringField(required=True)

    _meta = {
        'collection': 'pls',
        'allow_inheritance': False,
        'indexes': [{'fields':['slug'], 'unique': True},
                    {'fields':['sId'], 'unique': True},
                    {'fields':['city']},
                    {'fields':['-mOn']}
                    ]
        }

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'pls'
        if type(errors) == list:
            self._data['myErrors'] = errors
        else:

            # we want to generate a slug and make sure whatever slug may have been
            # given, if any, will be unique
            slugDefault = self.slug or self.dNamS or self.dNam
            self.slug = self.generate_slug(slugDefault)

            # turning off validation cause we do that in recurseValidateAndVOnUpSert
            kwargs['validate'] = False

            # this will return error if duplicate entries are attempted
            try:
                super(Pl, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e


    @staticmethod
    def vOnUpSert(d):
        errors = []
        d['dNam'] = d['city']
        if not 'dNamS' in d or not d['dNamS']:
            d['dNamS'] = d['dNam'].lower().replace(' ', '_')
        return {'doc_dict': d, 'errors': errors}
