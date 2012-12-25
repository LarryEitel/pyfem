# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils import myyaml, mdl
from utils.myyaml import postToMongo
import ctrs
import mdls
def cmpYml(yml, expect):
    i = 2
    while expect[i] == ' ': i += 1
    return yml == expect.replace(u' '*(i-1), '')

class CtrsLnkTests(BaseMongoTestCase):
    def test_add(self):
        g = self.g
        to_yaml = ctrs.d.to_yaml
        debug   = self.g['logger'].debug
        Put = ctrs.put.Put(g)
        Lnk = ctrs.lnk.Lnk(g)

        # start of cmd's to add/manipulate db
        resp = Put.cmd('push|Cmp.ni.emails|address:steve@apple.com|typ:work')
        #resp = Put.cmd('set|Prs.lwe|q:emails.address:bill@ms.com,emails.typ:work|address:steve@apple.com|typ:work')

        # Link kirmse to ni
        resp = Lnk.cmd('add|Cmp.kirmse|Cmp.ni|area-company')
        assert cmpYml(to_yaml(resp['response']['doc']), \
            '''
            Cmp.kirmse
              pars
                Cmp.ni
              pths
                Cmp.ni.company
            ''')

        # Link unit104 to kirmse
        resp = Lnk.cmd('add|Cmp.unit104|Cmp.kirmse|unit-area')
        assert cmpYml(to_yaml(resp['response']['doc']), \
            '''
            Cmp.unit104
              pars
                Cmp.kirmse
                  Cmp.ni
              pths
                Cmp.kirmse.area
                Cmp.ni.company
            ''')

        # Link troop1031 to unit104
        resp = Lnk.cmd('add|Cmp.troop1031|Cmp.unit104|troop-unit')
        assert cmpYml(to_yaml(resp['response']['doc']), \
            '''
            Cmp.troop1031
              pars
                Cmp.unit104
                  Cmp.kirmse
                    Cmp.ni
              pths
                Cmp.unit104.unit
                Cmp.kirmse.area
                Cmp.ni.company
            ''')


        # Link ni to atlanta-ga
        resp = Lnk.cmd('add|Cmp.ni|Pl.atlanta-ga|office')
        assert cmpYml(to_yaml(resp['response']['doc']), \
            '''
            Cmp.ni
              pars
                Pl.atlanta-ga
              pths
                Pl.atlanta-ga.office
              Children
                Cmp.kirmse
                  Cmp.unit104
                    Cmp.troop1031
            ''')

        _in_pths = ctrs.d.referenced_in_pths(resp['response']['doc'])
        # did Pl.atlanta-ga.office get added correctly to pths?
        assert cmpYml(_in_pths['_yml']['Cmp.unit104'], \
            '''
            Cmp.unit104
              pars
                Cmp.kirmse
                  Cmp.ni
                    Pl.atlanta-ga
              pths
                Cmp.kirmse.area
                Cmp.ni.company
                Pl.atlanta-ga.office
              Children
                Cmp.troop1031
            ''')


    def setUp(self):
        super(CtrsLnkTests, self).setUp()
        g = self.g
        me = g['me']
        self._clss        = g['_clss']
        self.post    = post    = ctrs.post.Post(g).post
        self.put     = put     = ctrs.put.Put(g).put
        self.lnkAdd  = lnkAdd  = ctrs.lnk.Lnk(g).add
        self.usecase = usecase = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsLnk')
        self.sampDat = sampDat = usecase['sampDat']

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