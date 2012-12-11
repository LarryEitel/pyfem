# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseMongoTestCase

class ModelsHelpers(BaseMongoTestCase):
    def setUp(self):
        super(ModelsHelpers, self).setUp()

    def test_prs(self):
        uc = self.usecase
        from models import Email, Prs

        uc.load('shiv_usecases1')
        cmds = uc.run_all('one')
        assert len(cmds) == 3


if __name__ == "__main__":
    unittest.main()