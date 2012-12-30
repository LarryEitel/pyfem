# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
import ctrs

class CtrsPutTests(BaseMongoTestCase):
    def test_tryToAddDupTypEmail(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Lnk = ctrs.lnk.Lnk()
        Post = ctrs.post.Post()

        # Load one doc
        Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')
        Put.cmd('push|Cmp.ni.emails|address:bill@ms.com')

        #try to add dup email
        resp = Put.cmd('push|Cmp.ni.emails|address:bill@ms.com')
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors']['address'] == 'address must be unique.'

    def test_tryToAddSecondPrimaryEmail(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Post = ctrs.post.Post()

        # Load one doc
        Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')
        Put.cmd('push|Cmp.ni.emails|address:bill@ms.com|prim:1')

        #try to add second primary
        resp = Put.cmd('push|Cmp.ni.emails|address:sue@ms.com|prim:1')
        assert resp['status'] == 500
        assert resp['response']['errors'][0]['errors']['prim'] == 'Only one permited primary item.'

    def test_add_one_to_empty_list(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Lnk = ctrs.lnk.Lnk()
        Post = ctrs.post.Post()

        # Load one doc
        resp = Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')

        # one new tel
        resp = Put.cmd('push|Cmp.ni.tels|text:123 456 7890|typ:work')
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['tels']
        assert targetElem[0]['text'] == '123 456 7890'


    def test_add_two_to_list(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Post = ctrs.post.Post()

        # Load one doc
        resp = Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')

        # new emails
        resp = Put.cmd('push|Cmp.ni.emails|address:bill@ms.com|typ:work')
        resp = Put.cmd('push|Cmp.ni.emails|address:william@ms.com|typ:home')
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails']
        assert len(targetElem) == 2
        assert targetElem[0]['address'] == 'bill@ms.com'

    def test_update(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Post = ctrs.post.Post()

        # Load one doc
        Post.cmd('Usr|slug:lwe|uNam:lwe|fNam:Larry|fNam2:Wayne|lNam:Stooge')
        Put.cmd('push|Usr.lwe.emails|address:bill@ms.com|typ:work')
        Put.cmd('push|Usr.lwe.emails|address:william@ms.com|typ:home')
        # put fNam & lNam
        resp = Put.cmd('set|Usr|q:slug:lwe|fNam:Sam|lNam:Hardy')
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        assert targetDoc['fNam'] == 'Sam'
        assert targetDoc['lNam'] == 'Hardy'

        # update existing email address
        resp = Put.cmd('set|Usr|q:slug:lwe,emails.address:bill@ms.com,emails.typ:work|emails.$.address:steve@apple.com|emails.$.typ:home')
        assert resp['status'] == 200
        targetDoc = resp['response']['doc']
        targetElem = targetDoc['emails'][0]
        assert targetElem['address'] ==  "steve@apple.com"

if __name__ == "__main__":
    unittest.main()