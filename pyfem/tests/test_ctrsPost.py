# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import ctrs
from utils import myyaml

class CtrsPostTests(BaseMongoTestCase):

    def setUp(self):
        super(CtrsPostTests, self).setUp()
        ucs          = self.usecase
        ucs.load('usecases')
        self.ucs     = ucs
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsPost')

    def test_newWithApths(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsLarryWayne']

        post    = ctrs.post.Post(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1
        #  cnts.update({"pths.pth" : "Prs.lwe,Cmp.ni"},{$set: {"pths.$.pth":"Prs.new"}})

    #TODOs
    # although testing is done in put to prevent multiple primary items in a list along with ability to prevent dup values like typ+address, THIS IS NOT TEST FOR POSTING new records. GOTTA RESOLVE and TEST

    def test_new(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsMoeStooge']

        post    = ctrs.post.Post(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_newUsr(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['UsrMoeStooge']

        post    = ctrs.post.Post(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_slug(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = ctrs.post.Post(self.g).post

        doc     = sampDat['PrsTryWithNoSlug']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200

        doc     = sampDat['PrsTryWithNoSlug2']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        if errors: print errors
        assert resp['status'] == 200
        doc = resp['response']['docs'][resp['response']['docs'].keys()[0]]
        assert doc['slug'] == 'stooge-moe-1'

    def test_trySlugDup(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = ctrs.post.Post(self.g).post

        doc     = sampDat['PrsMoeStooge']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200

        doc     = sampDat['PrsMoeStooge']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        doc = resp['response']['docs'][resp['response']['docs'].keys()[0]]
        assert doc['slug'] == 'stooge-moe-1'


    def test_tryNewPrsWithDupEmailTypAddress(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsInvalidWithDupEmailTryAddress']

        post    = ctrs.post.Post(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert status == 500
        assert errors[0]['errors']['address'] == 'address must be unique.'

    def test_tryNewPrsWithDupPrimListItem(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsInvalidWithDupPrimListItem']

        post    = ctrs.post.Post(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors'][0]['errors']['prim'] == 'Only one permited primary item.'
        x = 0

    def test_newSeveral(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = ctrs.post.Post(self.g).post

        # try several docs, EXCEPT items with Invalid in the key
        docs    = [sampDat[d] for d in sampDat if not 'Invalid' in d]
        resp    = post(**{'docs': docs})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(docs)

if __name__ == "__main__":
    unittest.main()