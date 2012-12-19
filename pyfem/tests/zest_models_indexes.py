# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from utils import myyaml
import controllers
from core import BaseMongoTestCase

class ModelsIndexesTests(BaseMongoTestCase):
    def setUp(self):
        super(ModelsIndexesTests, self).setUp()
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'models_indexes.yaml')

    # could not get consistent results on this
    def zest_tryToAddDupSlug(self):
        sampDat = self.sampDat

        post         = controllers.post.Post(self.g).post
        doc     = sampDat['PrsLarryStooge']

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert len(resp['response']['docs']) == 1

        # Load it again, this should fail cause index emails.prim is unique
        doc     = sampDat['PrsMoeStooge']
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 500

        assert resp['response']['errors'][0]['errors'].message == 'Tried to save duplicate unique keys (E11000 duplicate key error index: pyfem.cnts.$_types_1_slug_1  dup key: { : "MyDoc", : "LarryStooge" })'

        assert len(resp['response']['errors']) == 1


if __name__ == "__main__":
    unittest.main()