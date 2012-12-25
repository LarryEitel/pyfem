import datetime

from app import app
import mdls
from mdls import Mixin, D
from mdls.myfields import MyStringField
import helpers

import utils.name

class LnkRole(D, Mixin):
    '''Link Relationships'''
    fam      = app.me.BooleanField(help_text='Is Family Link/Relationship?')
    chldClss = app.me.ListField(MyStringField(help_text='Child Document class "_cls".'))
    chldGen  = MyStringField(help_text='Child Gender')
    chld     = MyStringField(help_text='Child Name/Title')
    parClss  = app.me.ListField(MyStringField(help_text='Parent Document class "_cls".'))
    parGen   = MyStringField(help_text='Parent Gender')
    par      = MyStringField(help_text='Parent Name/Title')
    mask     = MyStringField(help_text='Sharing Mask')
    w        = app.me.FloatField(help_text='Sort Weight')

    _meta = {
        'collection': 'lnkroles'
        }

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'lnkroles'
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
                super(LnkRole, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e
