# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils.myyaml import postToMongo
from utils import myyaml
import ctrs

class CtrlDTest(BaseMongoTestCase):

    # def test_tree(self):
    #     tree = self.tree
    #     resp = tree(**dict(_cls='Cmp', slug='ni'))
    #     pass

    def setUp(self):
        super(CtrlDTest, self).setUp()
        self.tree = ctrs.D(self.g).tree
        self.post    = post    = ctrs.post.Post(self.g).post
        self.put     = put     = ctrs.put.Put(self.g).put
        self.lnkAdd  = lnkAdd  = ctrs.lnk.Lnk(self.g).add
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