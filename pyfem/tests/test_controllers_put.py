# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
import controllers

class ControllersPutTests(BaseMongoTestCase):

    def setUp(self):
        super(ControllersPutTests, self).setUp()
        self.sampDat = myyaml.pyObj(self.tests_data_yaml_dir + 'controllers_put')

    def test_tryToAddDupTypEmail(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # one new email
        sampItem = sampDat['PrsTryToAddDupTypEmail']
        resp = put(**sampItem)
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors']['address'] == 'address must be unique.'
        x=0

    def test_tryToAddSecondPrimaryEmail(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # one new email
        sampItem = sampDat['PrsTryToAddSecondPrimaryEmail']
        resp = put(**sampItem)
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors']['prim'] == 'Only one permited primary item.'
        x=0

    def test_add_one_to_empty_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStoogeEmptyEmails']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # one new email
        sampItem = sampDat['PrsAddOneNewEmailToEmptyEmailsField']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails']
        assert len(targetElem) == 1
        assert targetElem[0]['address'] == 'timothy@ms.com'

    def test_add_two_to_empty_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStoogeEmptyEmails']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1


        # two new email
        sampItem = sampDat['PrsAddTwoNewEmailToEmptyEmailsField']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails']
        assert len(targetElem) == 2
        assert targetElem[1]['address'] == 'angie@ms.com'
        x=0

    def test_add_one_to_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # one new email
        sampItem = sampDat['PrsAddOneNewEmailToExistingEmailsField']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails']
        assert targetElem[2]['address'] == 'timothy@ms.com'
        assert len(targetElem) == 3
        x=0

    def test_add_two_to_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == 1

        # two new emails
        sampItem = sampDat['PrsAddTwoNewEmailsToExistingEmailsField']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails']
        assert targetElem[3]['address'] == 'sam@ms.com'
        assert len(targetElem) == 4
        x=0

    def test_update(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

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

        # update existing email address
        sampItem = sampDat['PrsPut_emails_1']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails'][0]
        assert targetElem['address'] ==  "freddy@ms.com"

        x=0


    def test_tryToSetSecondPrimEmail(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.post.Post(self.g).post
        put          = controllers.put.Put(self.g).put

        # Load one doc
        resp = post(**{'docs': [doc]})
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'][0] if not status == 200 else None
        assert status == 200
        assert len(resp['response']['docs']) == 1

        sampItem = sampDat['PrsTryToAddSecondPrimaryEmail']
        resp = put(**sampItem)
        status = resp['status']
        errors = resp['response']['errors'][0]['errors'] if not status == 200 else None
        assert resp['status'] == 500
        assert errors['prim'] == 'Only one permited primary item.'

        x=0


if __name__ == "__main__":
    unittest.main()