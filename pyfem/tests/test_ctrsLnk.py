# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml
from utils.myyaml import postToMongo, lTrimCompare
import ctrs
import mdls

class CtrsLnkTests(BaseMongoTestCase):
    def test_add(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Lnk = ctrs.lnk.Lnk()
        Post = ctrs.post.Post()

        # start of cmd's to add/manipulate db
        # here are a few
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


        # Link kirmse to ni
        resp = Lnk.cmd('add|Cmp.kirmse|Cmp.ni|area-company')
        assert lTrimCompare(to_yaml(resp['response']['doc']), \
            '''
            Cmp.kirmse
              pars
                Cmp.ni.area
              pths
                Cmp.ni.company: [Cmp.ni]
            ''')

        # Link unit104 to kirmse
        resp = Lnk.cmd('add|Cmp.unit104|Cmp.kirmse|unit-area')
        assert lTrimCompare(to_yaml(resp['response']['doc']), \
            '''
            Cmp.unit104
              pars
                Cmp.kirmse.unit
              pths
                Cmp.kirmse.area: [Cmp.kirmse]
                Cmp.ni.company: [Cmp.ni,Cmp.kirmse]
            ''')

        # Link troop1031 to unit104
        resp = Lnk.cmd('add|Cmp.troop1031|Cmp.unit104|troop-unit')
        assert lTrimCompare(to_yaml(resp['response']['doc']), \
            '''
            Cmp.troop1031
              pars
                Cmp.unit104.troop
              pths
                Cmp.unit104.unit: [Cmp.unit104]
                Cmp.kirmse.area: [Cmp.kirmse,Cmp.unit104]
                Cmp.ni.company: [Cmp.ni,Cmp.kirmse,Cmp.unit104]
            ''')


        # Link ni to atlanta-ga
        resp = Lnk.cmd('add|Cmp.ni|Pl.atlanta-ga|office')
        assert lTrimCompare(to_yaml(resp['response']['doc']), \
            '''
            Cmp.ni
              pars
                Pl.atlanta-ga.office
              pths
                Pl.atlanta-ga.office: [Pl.atlanta-ga]
              Children
                Cmp.kirmse
                  Cmp.unit104
                    Cmp.troop1031
            ''')

        _in_pths = ctrs.d.referenced_in_pths(resp['response']['doc'])
        ## did Pl.atlanta-ga.office get added correctly to pths?
        assert lTrimCompare(_in_pths['_yml']['Cmp.unit104'], \
            '''
            Cmp.unit104
              pars
                Cmp.kirmse.unit
              pths
                Cmp.kirmse.area: [Cmp.kirmse]
                Cmp.ni.company: [Cmp.ni,Cmp.kirmse]
                Pl.atlanta-ga.office: [Pl.atlanta-ga,Cmp.ni]
              Children
                Cmp.troop1031
            ''')


    def setUp(self):
        super(CtrsLnkTests, self).setUp()

if __name__ == "__main__":
    unittest.main()