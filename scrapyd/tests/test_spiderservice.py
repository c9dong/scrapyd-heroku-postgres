from twisted.trial import unittest
from mock import MagicMock
from mock import call
import subprocess
import sys

from zope.interface.verify import verifyObject

from scrapyd.services.spiderservice import SpiderService
from scrapyd.models.project import Project

class SpiderServiceTest(unittest.TestCase):
  def setUp(self):
    self.subprocess = MagicMock()
    self.cache = {}
    self.service = SpiderService(self.cache, self.subprocess)

  def test_getall_no_cache(self):
    mock_project = Project('a', '1')
    proc = MagicMock()
    proc.communicate = MagicMock(return_value=('s1\ns2\n', None))
    proc.returncode = None
    self.subprocess.Popen = MagicMock(return_value=proc)

    spiders = self.service.getall(mock_project)
    
    self.failUnlessEqual(spiders, ['s1', 's2'])
    self.failUnlessEqual(self.cache, {'a': {'1': ['s1', 's2']}})
    # check env args
    args, kwargs = self.subprocess.Popen.call_args
    env = kwargs['env']
    self.failUnlessEqual(env['PYTHONIOENCODING'], 'UTF-8')
    self.failUnlessEqual(env['SCRAPY_PROJECT'], 'a')
    self.failUnlessEqual(env['SCRAPY_EGG_VERSION'], '1')
    

  def test_getall_cache(self):
    mock_project = Project('a', '1')
    self.service._cache = {'a': {'1': ['s1', 's2']}}

    spiders = self.service.getall(mock_project)
    
    self.failUnlessEqual(spiders, ['s1', 's2'])

  def test_getall_noprocess(self):
    mock_project = Project('a', '1')
    proc = MagicMock()
    proc.communicate = MagicMock(return_value=('s1\ns2\n', None))
    proc.returncode = 1
    self.subprocess.Popen = MagicMock(return_value=proc)

    with self.assertRaises(RuntimeError):
      self.service.getall(mock_project)
