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

    def test_add_one_to_empty_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStoogeEmptyEmails']

        post         = controllers.generic_post.GenericPost(self.g).post
        put          = controllers.generic_put.GenericPut(self.g).put

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
        #assert targetElem[2]['dNam'] == 'work: timothy@ms.com'
        #assert len(targetElem) == 3
        x=0

    def test_add_one_to_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.generic_post.GenericPost(self.g).post
        put          = controllers.generic_put.GenericPut(self.g).put

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
        assert targetElem[2]['dNam'] == 'work: timothy@ms.com'
        assert len(targetElem) == 3
        assert targetElem[2]['eId'] == 3
        assert targetDoc['_eIds']['emails'] == 4
        x=0

    def test_add_two_to_list(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.generic_post.GenericPost(self.g).post
        put          = controllers.generic_put.GenericPut(self.g).put

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
        assert targetElem[3]['dNam'] == 'home: sam@ms.com'
        assert len(targetElem) == 4
        assert targetElem[3]['eId'] == 4
        assert targetDoc['_eIds']['emails'] == 5
        x=0

    def test_update(self):
        sampDat = self.sampDat

        doc = sampDat['PrsLarryStooge']

        post         = controllers.generic_post.GenericPost(self.g).post
        put          = controllers.generic_put.GenericPut(self.g).put

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
        assert targetDoc['dNam'] == 'Mary Smith'

        # put embedded note title
        sampItem = sampDat['PrsPut_emails_2_notes_1_title']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']['emails'][1]['notes'][0]
        assert targetDoc['title'] == sampItem['update']['actions']['$set']['flds']['title']
        assert 'mBy' in targetDoc
        assert targetDoc['dNam'] == 'work: New Title'

        # update emails[0] fields and add a notes list with a new note missing eId
        sampItem = sampDat['PrsPut_emails_1']
        resp = put(**sampItem)
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails'][0]
        assert targetElem['dNamS'] ==  "work__freddy@ms.com__prim"
        assert targetElem['notes'][0]['eId'] ==  1
        assert targetElem['_eIds']['notes'] ==  2

        x=0



if __name__ == "__main__":
    unittest.main()