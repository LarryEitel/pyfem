# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase

class ModelsTests(BaseMongoTestCase):
    def setUp(self):
        super(ModelsTests, self).setUp()

    def test_prs(self):
        uc = self.usecase
        from models import Email, Prs

        uc.load('usecases')
        cmds = uc.run_all('one')
        assert len(cmds) == 2


if __name__ == "__main__":
    unittest.main()