# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import controllers
from utils import myyaml

class TagsTests(BaseMongoTestCase):
    def setUp(self):
        super(TagsTests, self).setUp()
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'tags')


    def test_tagPost(self):
        sampDat = self.sampDat
        doc     = sampDat['TagCat']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1
        doc = resp['response']['docs'][resp['response']['docs'].keys()[0]]
        assert doc['slug'] == 'pet'

    def test_tagGrpPost(self):
        sampDat = self.sampDat
        doc     = sampDat['TagGrpPet']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1
        doc = resp['response']['docs'][resp['response']['docs'].keys()[0]]
        assert doc['slug'] == 'pet'



if __name__ == "__main__":
    unittest.main()