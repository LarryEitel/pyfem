from app import app
from mongoengine.base import ValidationError

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
        #self._meta['collection'] = 'cnts'
        #super(MyDoc, self).save(*args, **kwargs)


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


