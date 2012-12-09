# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
import controllers

class ControllersGenericPutTests(BaseMongoTestCase):

    def setUp(self):
        super(ControllersGenericPutTests, self).setUp()
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'controllers_generic_put')

    def test_put(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.generic_post.GenericPost(self.g).post
        put          = controllers.generic_put.GenericPut(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        #sampItem = sampDat['PrsPut_fNam']
        #resp = put(**sampItem)
        #assert resp['status'] == 200
        #respDoc = resp['response']['doc']
        #assert respDoc['fNam'] == sampItem['update']['flds']['fNam']['val']

        sampItem = sampDat['PrsPut_emails_2_notes_1']
        resp = put(**sampItem)
        assert resp['status'] == 200


        sampItem = sampDat['PrsPut_emails_2_typ']
        resp = put(**sampItem)
        assert resp['status'] == 200
        x=0



if __name__ == "__main__":
    unittest.main()