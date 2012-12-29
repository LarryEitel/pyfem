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
        Post.cmd('Pl|slug:ny-ny|city:New York')
        Post.cmd('Cmp|slug:ms|cNam:MS')
        Put.cmd('push|Cmp.ms.tels|text:123 456 7890|typ:work')
        Put.cmd('push|Cmp.ni.tels|text:123 456 7890|typ:work')
        Put.cmd('push|Cmp.ni.emails|address:steve@apple.com|typ:work')
        Put.cmd('set|Cmp|q:slug:ni,emails.address:steve@apple.com,emails.typ:work|emails.$.address:bill@ms.com|emails.$.typ:home')


        # Link kirmse to ni
        resp = Lnk.cmd('add|Cmp.kirmse|Cmp.ni|area-company')
        yml = to_yaml(resp['response']['doc'])
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

        # Link kirmse to Pl.ny-ny
        resp = Lnk.cmd('add|Cmp.kirmse|Pl.ny-ny|office')
        assert lTrimCompare(to_yaml(resp['response']['doc']), \
            '''
            Cmp.kirmse
              pars
                Cmp.ni.area
                Pl.ny-ny.office
              pths
                Cmp.ni.company: [Cmp.ni]
                Pl.atlanta-ga.office: [Pl.atlanta-ga,Cmp.ni]
                Pl.ny-ny.office: [Pl.ny-ny]
              Children
                Cmp.unit104
                  Cmp.troop1031
            ''')

        _in_pths = ctrs.d.referenced_in_pths(resp['response']['doc'])
        ## did Pl.ny-ny.office get added correctly to pths?
        assert lTrimCompare(_in_pths['_yml']['Cmp.troop1031'], \
            '''
            Cmp.troop1031
              pars
                Cmp.unit104.troop
              pths
                Cmp.unit104.unit: [Cmp.unit104]
                Cmp.kirmse.area: [Cmp.kirmse,Cmp.unit104]
                Cmp.ni.company: [Cmp.ni,Cmp.kirmse,Cmp.unit104]
                Pl.atlanta-ga.office: [Pl.atlanta-ga,Cmp.ni]
                Pl.ny-ny.office: [Pl.ny-ny,Cmp.kirmse]
            ''')
        x=0
    def test_trash(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put()
        Lnk = ctrs.lnk.Lnk()
        Post = ctrs.post.Post()
        Get = ctrs.get.Get()
        DS = ctrs.d.DS()

        if True:
            # start of cmd's to add/manipulate db
            # here are a few
            Post.cmd('Prs|slug:owner|fNam:John|lNam:Doe')
            Post.cmd('Cmp|slug:company|cNam:Company')
            Post.cmd('Cmp|slug:dept|cNam:Department')
            Post.cmd('Prs|slug:manager|fNam:Bill|lNam:Smith')
            Post.cmd('Prs|slug:employee|fNam:Tommy|lNam:Milton')
            Post.cmd('Pl|slug:atlanta-ga|city:Atlanta')
            Post.cmd('Pl|slug:ny-ny|city:New York')

            # test for valid _c
            # ie, Prs.owner. slug is owner, collection is cnts
            # BUT!!! _c needs to be confirmed
            Lnk.cmd('add|Cmp.company|Prs.owner|company-owner')
            Lnk.cmd('add|Cmp.dept|Cmp.company|dept-company')
            Lnk.cmd('add|Prs.manager|Cmp.dept|manager-dept')
            Lnk.cmd('add|Prs.employee|Prs.manager|employee-manager')

        docs = Get.cmd('cnts')
        DS.listDocs(docs)

        # this is the before trash action
        doc = Get.cmd('cnts:1|q:slug:owner')
        assert lTrimCompare(to_yaml(doc), \
            '''
            Prs.owner
              Children
                Cmp.company
                  Cmp.dept
                    Prs.manager
                      Prs.employee
            ''')

        doc = Get.cmd('cnts:1|q:slug:company')
        assert lTrimCompare(to_yaml(doc), \
            '''
            Cmp.company
              pars
                Prs.owner.company
              pths
                Prs.owner.owner: [Prs.owner]
              Children
                Cmp.dept
                  Prs.manager
                    Prs.employee
            ''')

        doc = Get.cmd('cnts:1|q:slug:employee')
        assert lTrimCompare(to_yaml(doc), \
            '''
            Prs.employee
              pars
                Prs.manager.employee
              pths
                Prs.manager.manager: [Prs.manager]
                Cmp.dept.dept: [Cmp.dept,Prs.manager]
                Cmp.company.company: [Cmp.company,Cmp.dept,Prs.manager]
                Prs.owner.owner: [Prs.owner,Cmp.company,Cmp.dept,Prs.manager]
            ''')

        # trash lnk
        # direct call
        resp = Lnk.trash(**dict(chld_=dict(_c='Cmp', slug='company'), par_= dict(_c='Prs', slug='owner'), role_='company-owner'))
        resp['response']['doc']['pars'][0]['trash'] == True


        # using cmd shortcut
        # TODO: create Put.recycle to unset trash field
        resp = Put.cmd('set|Cmp|q:slug:company|pars.0.trash:0')

        resp = Lnk.cmd('del|Cmp.company|Prs.owner|company-owner')
        resp['response']['doc']['pars'][0]['trash'] == True


        # check at least one of doc.pths that should now have trash = True
        doc = Get.cmd('cnts:1|q:slug:employee')
        doc['pths'][3]['trash'] == True


        #docs = Get.cmd('cnts|q:_c:Usr|vflds:1')
        docs = Get.cmd('cnts|vflds:1')
        PyYaml.dump(docs, logCollNam='cnts', allflds=True)
        # PyYaml.dump(docs, logCollNam='cnts', onlyflds=['vNam'])
        # PyYaml.dump(docs, logCollNam='cnts', onlyflds=['_c','vNam','slug','pars'])


        x=0

    def setUp(self):
        super(CtrsLnkTests, self).setUp()

if __name__ == "__main__":
    unittest.main()