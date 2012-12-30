# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import ctrs
from utils import myyaml

class CtrsPostTests(BaseMongoTestCase):

    def setUp(self):
        super(CtrsPostTests, self).setUp()
        ucs          = self.usecase
        ucs.load('usecases')
        self.ucs     = ucs
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsPost')

    def test_new(self):
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Post = ctrs.post.Post()

        #resp = Post.post(**{'docs': [{'_types': ['Prs'], 'lNam': 'Doe', '_cls': 'Prs', 'fNam': 'John', '_c': 'Prs', 'slug': 'jonndoe'}]})
        resp = Post.cmd('Prs|slug:jonndoe|fNam:John|lNam:Doe')
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_newUsr(self):
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Post = ctrs.post.Post()

        resp = Post.cmd('Usr|slug:johndoe|uNam:johndoe|fNam:John|lNam:Doe')
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_slug(self):
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Post = ctrs.post.Post()

        resp = Post.cmd('Usr|uNam:johndoe|fNam:John|lNam:Doe')
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert [v for v in resp['response']['docs'].itervalues()][0]['slug'] == 'doe-john'

        # try with same slug, it should increment
        resp = Post.cmd('Usr|slug:doe-john|uNam:johndoe2|fNam:John|lNam:Doe')
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert [v for v in resp['response']['docs'].itervalues()][0]['slug'] == 'doe-john-1'

    def test_newSeveral(self):
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Post = ctrs.post.Post()

        resp = Post.cmd([
            'Usr|uNam:johndoe|fNam:John|lNam:Doe',
            'Prs|fNam:Mary|lNam:Jane',
            'Cmp|cNam:MS',
                         ])

        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 3

if __name__ == "__main__":
    unittest.main()