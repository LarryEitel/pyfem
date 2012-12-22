# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
from utils.myyaml import postToMongo
import ctrs
import mdls

class CtrsLnkTests(BaseMongoTestCase):
    def test_put(self):
        post    = self.post
        put     = self.put
        lnkPut  = self.lnkPut
        sampDat = self.sampDat
        dos     = self.dos

        do = dos['put__Cmp.kirmse_Cmp.ni_dept-company']

        # Load one doc
        resp = lnkPut(**do)
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        x=0

    def setUp(self):
        super(CtrsLnkTests, self).setUp()
        self.post    = post    = ctrs.post.Post(self.g).post
        self.put     = put     = ctrs.put.Put(self.g).put
        self.lnkPut  = lnkPut  = ctrs.lnk.Lnk(self.g).put
        self.usecase = usecase = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsLnk')
        self.sampDat = sampDat = usecase['sampDat']
        self.dos = usecase['dos']

        # load lnkroles
        resp = postToMongo(post, self.data_dir + 'lnkroles')
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(resp['response']['yamlData']['data'])

        # load sample initial data
        for item in sampDat['initload'].itervalues():
            self.asrt(post(item))

    def asrt(self, cmd):
        resp = cmd
        if not resp['status'] == 200:
            print resp['response']['errors'][0]
        assert resp['status'] == 200

if __name__ == "__main__":
    unittest.main()