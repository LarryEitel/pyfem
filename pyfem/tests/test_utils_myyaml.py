# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase
from utils.myyaml import loadMongoCollection
from utils import myyaml
import controllers

class UtilsMyYamlTest(BaseMongoTestCase):
    def setUp(self):
        super(UtilsMyYamlTest, self).setUp()

    def test_loadMongoCollection(self):
        uc.load('usecases')


if __name__ == "__main__":
    unittest.main()