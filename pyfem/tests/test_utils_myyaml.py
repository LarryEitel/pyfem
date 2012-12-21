# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils.myyaml import postToMongo
from utils import myyaml
import ctrs

class UtilsMyYamlTest(BaseMongoTestCase):
    def setUp(self):
        super(UtilsMyYamlTest, self).setUp()

    def test_postToMongo(self):
        post = ctrs.post.Post(self.g).post
        resp = postToMongo(post, self.data_dir + 'lnkroles')
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(resp['response']['yamlData']['data'])


if __name__ == "__main__":
    unittest.main()