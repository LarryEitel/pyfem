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


    #TODOs
    # although testing is done in put to prevent multiple primary items in a list along with ability to prevent dup values like typ+address, THIS IS NOT TEST FOR POSTING new records. GOTTA RESOLVE and TEST

    def test_post_new_one(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsMoeStooge']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

    def test_slug_generator(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = controllers.generic_post.GenericPost(self.g).post

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
        assert doc['slug'] == 'moestooge-1'

    def test_tryDupSlug(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = controllers.generic_post.GenericPost(self.g).post

        doc     = sampDat['PrsMoeStooge']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 200

        doc     = sampDat['PrsMoeStooge']
        resp    = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        if errors: print errors
        assert resp['status'] == 200
        doc = resp['response']['docs'][resp['response']['docs'].keys()[0]]
        assert doc['slug'] == 'moestooge-1'


    def test_tryToPostPrsWithDupEmailTryAddress(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsInvalidWithDupEmailTryAddress']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors'][0]['errors']['typ+address'] == 'typ+address must be unique.'
        x = 0

    def test_tryToPostPrsWithDupPrimListItem(self):
        ucs     = self.ucs
        sampDat = self.sampDat
        doc     = sampDat['PrsInvalidWithDupPrimListItem']

        post    = controllers.generic_post.GenericPost(self.g).post

        # try one doc
        resp    = post(**{'docs': [doc]})
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors'][0]['errors']['prim'] == 'Only one permited primary item.'
        x = 0

    def test_post_new_several(self):
        ucs     = self.ucs
        sampDat = self.sampDat

        post    = controllers.generic_post.GenericPost(self.g).post

        # try several docs, EXCEPT items with Invalid in the key
        docs    = [sampDat[d] for d in sampDat if not 'Invalid' in d]
        resp    = post(**{'docs': docs})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(docs)

if __name__ == "__main__":
    unittest.main()