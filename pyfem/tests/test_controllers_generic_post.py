# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import controllers
from utils import myyaml

class ControllersGenericPostTests(BaseMongoTestCase):

    def setUp(self):
        super(ControllersGenericPostTests, self).setUp()
        ucs          = self.usecase
        ucs.load('usecases')
        self.ucs     = ucs
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'controllers_generic_post')

    def test_post_new_one(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsMoeStooge']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_post_new_several(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = controllers.generic_post.GenericPost(self.g).post

        # try several docs
        docs    = sampDat.values()[:1]
        resp    = post(**{'docs': docs})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(docs)

if __name__ == "__main__":
    unittest.main()