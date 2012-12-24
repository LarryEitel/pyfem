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

class CtrsLnkTests(BaseMongoTestCase):
    def test_add(self):
        post    = self.post
        put     = self.put
        lnkAdd  = self.lnkAdd
        #tree    = self.tree2
        #tree2    = self.tree2
        sampDat = self.sampDat
        dos     = self.dos
        debug   = self.g['logger'].debug

        # Link kirmse to ni
        do = dos['lnkAdd|Cmp.kirmse|Cmp.ni|area-company']
        resp = lnkAdd(**do['test'])
        status = resp['status']
        assert status == 200
        doc = resp['response']['doc']
        assert '_id' in doc
        for fld, val in do['expect']['flds'].iteritems():
            assert doc[fld] == val
        for expr, val in do['expect']['evals'].iteritems():
            assert eval(expr) == val

        # Link unit104 to kirmse
        do = dos['lnkAdd|Cmp.unit104|Cmp.kirmse|unit-area']
        resp = lnkAdd(**do['test'])
        status = resp['status']
        assert status == 200
        doc = resp['response']['doc']
        assert '_id' in doc
        for fld, val in do['expect']['flds'].iteritems():
            assert doc[fld] == val
        for expr, val in do['expect']['evals'].iteritems():
            assert eval(expr) == val

        # Link troop1031 to unit104
        do = dos['lnkAdd|Cmp.troop1031|Cmp.unit104|troop-unit']
        resp = lnkAdd(**do['test'])
        status = resp['status']
        assert status == 200
        doc = resp['response']['doc']
        assert '_id' in doc
        for fld, val in do['expect']['flds'].iteritems():
            assert doc[fld] == val
        for expr, val in do['expect']['evals'].iteritems():
            assert eval(expr) == val

        # Link ni to atlanta-ga
        do = dos['lnkAdd|Cmp.ni|Pl.atlanta-ga|office']
        resp = lnkAdd(**do['test'])
        status = resp['status']
        assert status == 200
        doc = resp['response']['doc']
        assert '_id' in doc
        for fld, val in do['expect']['flds'].iteritems():
            assert doc[fld] == val
        for expr, val in do['expect']['evals'].iteritems():
            assert eval(expr) == val

        _in_pths = ctrs.d.referenced_in_pths(doc)
        # did pths get added correctly?
        x=0


    def setUp(self):
        super(CtrsLnkTests, self).setUp()
        g = self.g
        db = g['db']
        self.mgodb        = db.connection[db.app.config['MONGODB_DB']]
        self._clss        = self.g['_clss']
        self.post    = post    = ctrs.post.Post(self.g).post
        self.put     = put     = ctrs.put.Put(self.g).put
        self.lnkAdd  = lnkAdd  = ctrs.lnk.Lnk(self.g).add
        #self.tree    = tree    = ctrs.d.D(self.g, 1, 1).tree
        #self.tree2    = tree2    = ctrs.d.D(self.g, 1, 1).tree2
        self.usecase = usecase = myyaml.pyObj(self.tests_data_yaml_dir + 'ctrsLnk')
        self.sampDat = sampDat = usecase['sampDat']
        self.dos = usecase['dos']

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