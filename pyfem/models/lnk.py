import datetime

from app import app
import models
from models import Mixin, MyDoc
from models.myfields import MyStringField
import helpers

import utils.name

class LnkRel(MyDoc, Mixin):
    '''Link Relationships'''
    fam      = app.db.BooleanField(help_text='Is Family Link/Relationship?')
    chld_clss = app.db.ListField(MyStringField(help_text='Child Document class "_cls".'))
    chldGen  = MyStringField(help_text='Child Gender')
    chldNam  = MyStringField(help_text='Child Name/Title')
    chldNamS = MyStringField(help_text='Child Name/Title Short')
    par_clss  = app.db.ListField(MyStringField(help_text='Parent Document class "_cls".'))
    parGen   = MyStringField(help_text='Parent Gender')
    parNam   = MyStringField(help_text='Parent Name/Title')
    parNamS  = MyStringField(help_text='Parent Name/Title Short')
    mask     = MyStringField(help_text='Sharing Mask')
    w        = app.db.FloatField(help_text='Sort Weight')

    _meta = {
        'collection': 'lnkrels'
        }

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'lnkrels'
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
                super(LnkRel, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e
