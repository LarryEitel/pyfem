# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils.myyaml import postToMongo, PyYaml
from utils import myyaml
import ctrs
from load_sample_data import scenario_1

class UtilsMyYamlTest(BaseMongoTestCase):
    def setUp(self):
        super(UtilsMyYamlTest, self).setUp()

    def test_postToMongo(self):
        post = ctrs.post.Post().post
        resp = postToMongo(post, self.data_dir + 'lnkroles')
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(resp['response']['yamlData']['data'])


    def test_MongoToYaml(self):
        Get = ctrs.get.Get()
        scenario_1()

        #docs = Get.cmd('cnts|q:_c:Usr|vflds:1')
        docs = Get.cmd('cnts')
        PyYaml.dump(docs, logCollNam='cnts', allflds=True)


if __name__ == "__main__":
    unittest.main()