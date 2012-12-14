import re
from app import app
from mongoengine.base import ValidationError
from utils.name import slug

def validDocData(m):
    '''Return dict with model _data that actually valid. doc._data contains invalid data.'''
    m_data = m._data
    data = {}
    for k, v in m_data.iteritems():
        if v and k:
            data[k] = v

    # make sure these are set
    data['_cls'] = m._cls
    data['_types'] = [m._cls]
    return data

def validate(doc):
    # Get a list of tuples of field names and their current values
    fields = [(field, getattr(doc, name))
              for name, field in doc._fields.items()]

    # Ensure that each field is matched to a valid value
    errors = {}
    for field, value in fields:
        if value is not None:
            try:
                field._validate(value)
                # need to capture field-level errors!
                if hasattr(field, 'myError'):
                    errors[field.name] = field.myError
                    # del it not that we have captured the error
                    del field.myError
            except ValidationError, error:
                errors[field.name] = error.errors or error
            except (ValueError, AttributeError, AssertionError), error:
                errors[field.name] = error
        elif field.required:
            errors[field.name] = ValidationError('Field is required',
                                                 field_name=field.name)
    return errors

def test_hook(m):
    return True

class BaseDocMixin(object):
    def validDocData(self):
        return validDocData(self)

    _pre_save_hooks = [
            test_hook,
            validate
        ]

    def pre_save(self, *args, **kwargs):
        for hook in self._pre_save_hooks:
            # the callable can raise an exception if
            # it determines that it is inappropriate
            # to save this instance; or it can modify
            # the instance before it is saved
            hook(self)
        super(MyDoc, self).save(*args, **kwargs)


# inspired by http://stackoverflow.com/questions/6102103/using-mongoengine-document-class-methods-for-custom-validation-and-pre-save-hook
class MyDoc(app.db.Document, BaseDocMixin):

    _meta = {
        'allow_inheritance': True
        }

    def validate(self):
        return validate(self)
    # http://stackoverflow.com/questions/6102103/using-mongoengine-document-class-methods-for-custom-validation-and-pre-save-hook

    #def save(self, *args, **kwargs):
        #super(MyDoc, self).save(*args, **kwargs)

    def generate_slug(self, value):
        """Query the database for similarly matching values. Then
        increment the maximum trailing integer. In the future this
        will rely on map-reduce(?).

        This method first makes a basic slug from the given value.
        Then it checks to see if any documents in the database share
        that same value in the same field. If it finds matching
        results then it will attempt to increment the counter on the
        end of the slug.

        It uses pymongo directly because mongoengine's own querysets
        rely on each field's __set__ method, which results in endless
        recrusion.
        """
        collection = self.__class__.objects._collection
        slugVal = slug(value)
        slug_regex = '^%s' % slugVal
        existing_docs = [
            {'id': doc['_id'], 'slug': doc['slug']} for doc in
            collection.find({'slug': {'$regex':slug_regex}})
        ]
        matches = [int(re.search(r'-[\d]+$', doc['slug']).group()[-1:])
            for doc in existing_docs if re.search(r'-[\d]+$', doc['slug'])]

        # Four scenarios:
        # (1) No match is found, this is a brand new slug
        # (2) A matching document is found, but it's this one
        # (3) A matching document is found but without any number
        # (4) A matching document is found with an incrementing value
        next = 1
        if len(existing_docs) == 0:
            return slugVal
        elif self.id in [doc['id'] for doc in existing_docs]:
            return self['slug']
        elif not matches:
            return u'%s-%s' % (slugVal, next)
        else:
            next = max(matches) + 1
            return u'%s-%s' % (slugVal, next)





class MyEmbedDoc(app.db.EmbeddedDocument, BaseDocMixin):
    def validDocData(self):
        return validDocData(self)

    def validate(self):
        return validate(self)

    _pre_save_hooks = [
            test_hook,
            validate
        ]
    def pre_save(self, *args, **kwargs):
        for hook in self._pre_save_hooks:
            # the callable can raise an exception if
            # it determines that it is inappropriate
            # to save this instance; or it can modify
            # the instance before it is saved
            hook(self)
        super(MyDoc, self).save(*args, **kwargs)

    # http://stackoverflow.com/questions/6102103/using-mongoengine-document-class-methods-for-custom-validation-and-pre-save-hook
    #def save(self, *args, **kwargs):
        #super(MyEmbedDoc, self).save(*args, **kwargs)


