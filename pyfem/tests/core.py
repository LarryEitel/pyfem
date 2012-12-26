# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import datetime
import random
import os
import usecase
import usecase1
import globals
import ctrs
from utils.myyaml import postToMongo


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        from app import app
        from util import now

        # app.config.from_object('default_settings')
        # app.config['MONGODB_DB'] = 'pyfem_unittest'
        app.config['DEBUG'] = True
        app.config['TESTING'] = True

        self.config = app.config
        self.app = app.test_client()
        self.flask_app = app

        self.used_keys = []
        self.now = now

class BaseMongoTestCase(unittest.TestCase):
    def setUp(self):
        from app import app
        from util import now

        self.tests_data_yaml_dir = app.config['HOME_PATH'] + 'tests/data/yaml/'
        self.data_dir            = app.config['HOME_PATH'] + 'data/'
        self.usecase             = usecase.UseCase(self.tests_data_yaml_dir)
        self.usecase1            = usecase.UseCase(self.tests_data_yaml_dir)

        self.config = app.config

        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        self._flush_db()

        g           = globals.load()
        g['usr']    = {"OID": "50468de92558713d84b03fd7", "at": (-84.163063, 9.980516)}
        g['me']      = app.me
        g['pymongo'] = app.pymongo
        g['logger'] = app.logger
        self.g = g
        app.g = g



        # load lnkroles
        resp = postToMongo(ctrs.post.Post().post, self.data_dir + 'lnkroles')
        assert resp['status'] == 200
        assert len(resp['response']['docs']) == len(resp['response']['yamlData']['data'])



    def tearDown(self):
        #self._flush_db()
        pass

    def _flush_db(self):
        from mongoengine.connection import _get_db
        me = _get_db()
        #Truncate/wipe the test database
        names = [name for name in me.collection_names() \
            if 'system.' not in name]
        [me.drop_collection(name) for name in names]

    def _get_target_url(self):
        raise NotImplementedError

    def _get_target_class(self):
        raise NotImplementedError

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_card_class(self):
        from mdls import Kard
        return Kard

    def _get_record_class(self):
        from mdls import DailyRecord
        return DailyRecord

    def _make_unique_key(self):
        key = random.randint(1, 10000)
        if key not in self.used_keys:
            self.used_keys.append(key)
            return key
        return self._make_unique_key()

    def assertEqualDateTimes(self, expected, actual):
        expected = (expected.year, expected.month, expected.day, expected.hour, expected.minute)
        actual = (actual.year, actual.month, actual.day, actual.hour, actual.minute)
        self.assertEqual(expected, actual)
