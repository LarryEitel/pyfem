# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import controllers

class ControllersGenericPostTests(BaseMongoTestCase):

    def setUp(self):
        super(ControllersGenericPostTests, self).setUp()
        ucs = self.usecase
        ucs.load('usecases')
        self.ucs = ucs

    def test_post_new(self):
        ucs = self.ucs
        samp_prss = ucs.uc_dat['prs']
        larry_stooge = samp_prss['larry_stooge']

        fn = controllers.generic_post.GenericPost(self.g)

        # try one doc
        resp = fn.post(**{'docs': [larry_stooge]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # try several docs
        multiple_docs = samp_prss.values()[:1]
        resp = fn.post(**{'docs': multiple_docs})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(multiple_docs)

if __name__ == "__main__":
    unittest.main()