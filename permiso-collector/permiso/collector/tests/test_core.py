from twisted.trial import unittest

from twisted.python import log
from twisted.python import failure

from twisted.internet import reactor

class CoreTest(unittest.TestCase):
    def setUp(self):
        print "setUp : rien faire"
    def tearDown(self):
        print "tearDown : Rien faire"

    def testMyFunction1(self):
        assert 3 == 3
