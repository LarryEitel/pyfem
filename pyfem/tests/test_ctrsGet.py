# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
from utils.myyaml import postToMongo, lTrimCompare, PyYaml
import ctrs
import mdls

class CtrsGetTests(BaseMongoTestCase):
    def test_get_one(self):
        Get = ctrs.get.Get()
        DS = ctrs.d.DS()

        #docs = Get.cmd('cnts')
        #PyYaml.dump(docs, logCollNam='cnts', allflds=True)

        doc = Get.cmd('cnts:1|q:slug:ni')

        #docs = Get.cmd('cnts')
        PyYaml.dump([doc], logCollNam='cnts', allflds=True)

        assert True

        doc = Get.get_one(**dict(collNam='cnts', query=dict(_c='Usr'), vflds=True))
        assert doc['vNam'] == u"Stooge, Larry Wayne"
        doc = Get.cmd('cnts:1|q:_c:Usr|vflds:1')
        assert doc['vNam'] == u"Stooge, Larry Wayne"

    def test_get(self):
        Get = ctrs.get.Get()
        DS = ctrs.d.DS()

        docs = Get.get(**dict(collNam='cnts', query=dict(_c='Usr'), vflds=True))
        assert docs[0]['vNam'] == u"Stooge, Larry Wayne"
        docs = Get.cmd('cnts|q:_c:Usr|vflds:1')
        assert docs[0]['vNam'] == u"Stooge, Larry Wayne"

        docs = Get.get(**dict(collNam='cnts', query=dict(_c='Usr'), fields='fNam, lNam,_id:0'))
        assert len(docs[0].keys()) == 4
        docs = Get.cmd('cnts|q:_c:Usr|fields:fNam,lNam,_id:0')
        assert len(docs[0].keys()) == 4

        docs = Get.get(**dict(collNam='cnts', query=dict(_c='Cmp'), sorts='cNam-1'))
        assert docs[0]['cNam'] == u"New Name"
        docs = Get.cmd('cnts|q:_c:Cmp|sorts:cNam-1')
        assert docs[0]['cNam'] == u"New Name"

        docs = Get.get(**dict(collNam='cnts', skip=2, limit=2))
        assert len(docs) == 2
        docs = Get.cmd('cnts|skip:2|limit:2')
        assert len(docs) == 2

        docs = Get.get(**dict(collNam='cnts', query={'emails.address':'bill@ms.com'}))
        assert docs[0]['emails'][0]['address'] == u"bill@ms.com"
        docs = Get.cmd('cnts|q:emails.address:bill@ms.com|fields:cNam,emails,_id:0|sorts:cNam-1|vflds:1|skip:0|limit:1')
        assert docs[0]['emails'][0]['address'] == u"bill@ms.com"

        #DS.listDocs(docs)
        pass

    def setUp(self):
        super(CtrsGetTests, self).setUp()
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Lnk = ctrs.lnk.Lnk()
        Post = ctrs.post.Post()

        Post.cmd('Usr|slug:lwe|uNam:lwe|fNam:Larry|fNam2:Wayne|lNam:Stooge')
        Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')
        Post.cmd('Cmp|slug:kirmse|cNam:Kirmse|typ:area')
        Post.cmd('Cmp|slug:unit104|cNam:104|typ:unit')
        Post.cmd('Cmp|slug:troop1031|cNam:1031|typ:troop')
        Post.cmd('Pl|slug:atlanta-ga|city:Atlanta')
        Post.cmd('Cmp|slug:ms|cNam:MS')
        Put.cmd('push|Cmp.ms.tels|text:123 456 7890|typ:work')
        Put.cmd('push|Cmp.ni.tels|text:123 456 7890|typ:work')
        Put.cmd('push|Cmp.ni.emails|address:steve@apple.com|typ:work')
        Put.cmd('set|Cmp|q:slug:ni,emails.address:steve@apple.com,emails.typ:work|emails.$.address:bill@ms.com|emails.$.typ:home')
        Put.cmd('set|Cmp|q:slug:ni|cNam:New Name')
        Lnk.cmd('add|Cmp.kirmse|Cmp.ni|area-company')
        Lnk.cmd('add|Cmp.unit104|Cmp.kirmse|unit-area')
        Lnk.cmd('add|Cmp.troop1031|Cmp.unit104|troop-unit')
        Lnk.cmd('add|Cmp.ni|Pl.atlanta-ga|office')



if __name__ == "__main__":
    unittest.main()