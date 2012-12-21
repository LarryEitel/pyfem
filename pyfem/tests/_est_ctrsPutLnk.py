# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
import ctrs

class CtrsPutLnkTests(BaseMongoTestCase):

    def setUp(self):
        super(CtrsPutLnkTests, self).setUp()
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsPutLnk')

    def test_update(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = ctrs.post.Post(self.g).post
        put          = ctrs.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # put fNam & lNam
        sampItem = sampDat['PrsPut_fNam']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        assert targetDoc['fNam'] == sampItem['update']['actions']['$set']['flds']['fNam']

        x=0


if __name__ == "__main__":
    unittest.main()