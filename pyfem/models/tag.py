import datetime
from app import app
from models import Mixin, MyDoc
from models.myfields import MyStringField
import helpers

class TagGrp(MyDoc, Mixin):
    # model classes that this tag type is relavent
    # famTags
    # hobbyTags
    # skillTags
    # bio
    # pets
    clss = app.db.ListField(MyStringField(), required= True)
    '''Tag model classes for which this tagGrp is relevant'''

    _meta = {
        'collection': 'taggrps'
        }

    @staticmethod
    def vOnUpSert(d):
        errors = []
        if not 'dNamS' in d or not d['dNamS']:
            d['dNamS'] = d['dNam'].lower().replace(' ', '_')
        return {'doc_dict': d, 'errors': errors}

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'taggrps'
        if type(errors) == list:
            self._data['myErrors'] = errors
        else:

            if not self.slug:
                self.slug = self.generate_slug(self.dNamS)

            # turning off validation cause we do that in recurseValidateAndVOnUpSert
            kwargs['validate'] = False

            # this will return error if duplicate entries are attempted
            try:
                super(TagGrp, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e

class Tag(MyDoc, Mixin):
    tagGrp = MyStringField()
    tag = MyStringField()
    _meta = {
        'collection': 'tags'
        }

    @staticmethod
    def vOnUpSert(d):
        # NOTE: What to do about foreign ref to tagGrp.
        # may use par/chld approach. Achieves more robust hierarchy
        errors = []
        if not 'dNam' in d:
            d['dNam'] = d['tagGrp'] + '.' + d['tag']
        if not 'dNamS' in d or not d['dNamS']:
            d['dNamS'] = d['dNam'].lower().replace(' ', '_')
        return {'doc_dict': d, 'errors': errors}

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()

        if not self.id:
            self.cOn = self.oOn = now

        self.mOn = now

        errors = helpers.recurseValidateAndVOnUpSert(self)

        self._meta['collection'] = 'tags'
        if type(errors) == list:
            self._data['myErrors'] = errors
        else:

            if not self.slug:
                self.slug = self.generate_slug(self.dNamS)

            # turning off validation cause we do that in recurseValidateAndVOnUpSert
            kwargs['validate'] = False

            # this will return error if duplicate entries are attempted
            try:
                super(Tag, self).save(*args, **kwargs)
            except Exception, e:
                self._data['myErrors'] = e
