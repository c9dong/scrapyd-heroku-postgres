from twisted.internet.defer import inlineCallbacks, maybeDeferred
from twisted.trial import unittest
from mock import MagicMock

from zope.interface.verify import verifyObject

from scrapyd.queues.queue import ISpiderQueue
from scrapyd.queues.queue import SpiderQueue

class SpiderQueueTest(unittest.TestCase):
    """This test case also supports queues with deferred methods.
    """

    def setUp(self):
        self.db = MagicMock()
        self.q = SpiderQueue(self.db)
        self.name = 'spider1'
        self.args = {
            'arg1': 'val1',
            'arg2': 2,
            'arg3': u'\N{SNOWMAN}',
        }
        self.msg = self.args.copy()
        self.msg['name'] = self.name


    def test_interface(self):
        verifyObject(ISpiderQueue, self.q)

    def test_add(self):
        args = {
            'arg1': '1',
            'priority': 2
        }
        name = 'table'
        self.q.add(name, **args)
        self.db.put.assert_called_with({'arg1': '1', 'name': name}, 2)

    def test_pop(self):
        self.q.pop()
        self.db.pop.assert_called()

    def test_count(self):
        self.db.__len__.return_value = 1
        l = self.q.count()
        self.assertEqual(l, 1)

    def test_list(self):
        dbdata = [1,2,3,4,5,6,7,8,9]
        self.db.__iter__.return_value = ([i] for i in dbdata)
        data = self.q.list()
        self.assertEqual(data, dbdata)

    def test_remove(self):
        func = lambda d : True
        self.q.remove(func)
        self.db.remove.assert_called_with(func)

    def test_clear(self):
        self.q.clear()
        self.db.clear.assert_called()
