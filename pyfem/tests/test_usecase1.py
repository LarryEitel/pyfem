# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import datetime
from copy import deepcopy
from core import BaseTestCase, BaseMongoTestCase
from bson import ObjectId
from utils import myyaml
from utils.myyaml import postToMongo
import ctrs
import mdls


class UseCase1Tests(BaseMongoTestCase):
    def test_run(self):
        post    = self.post
        put     = self.put
        sampDat = self.sampDat


        '''
            # link Usr.lwe to Cmp.ni as admin
            put Usr.lwe.pars, $push, Cmp.ni, admin
            put Usr.lwe.pars, $push, Pl.pllwe, home
            put Cmp.ni.pars, $push, Pl.plni, office
            put Cmp.prggrp.pars, $push, Cmp.ni, department
            put Cmp.kirmse.pars, $push, Cmp.ni, department
            put Cmp.unit104.pars, $push, Cmp.kirmse, area
            put Cmp.troop1031.pars, $push, Cmp.unit104, unit
            put Usr.sallysmith.pars, $push, Cmp.kirmse, admin
            put Usr.sallysmith.pars, $push, Cmp.troop1031, troop_leader
            put Usr.suziebell.pars, $push, Cmp.troop1031, brownie

            # what will do? To children?
            put Cmp.unit104.pars, $push, Pl.plni2, annex
            # unit104 should see two Pl's:
                office: Pl.plni
                annex: Pl.plni2

            delete Usr.sallysmith.pars, $unset, Usr.sallysmith
            put Usr.suziebell.pars.Cmp.troop1031, $set, role, troop_leader

            get Cmp.troop1031.pars ??? cls==Pl # how to get Pl coming from ni

            # get Places for Usr.lwe
            get Usr.lwe.pars ??? cls==Pl
            '''





        # sampItem = sampDat['lwe_ni']
        # resp = put(**sampItem)
        #assert put(**{'src': 'Usr.lwe', 'dst': 'Cmp.ni', 'lnkRel': 'admin.employer'})['status'] == 200

        pass


    def setUp(self):
        super(UseCase1Tests, self).setUp()
        self.post = post = ctrs.post.Post(self.g).post
        self.put  = put  = ctrs.put.Put(self.g).put
        self.usecase = usecase = myyaml.pyObj(self.tests_data_yaml_dir + 'usecase1')
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