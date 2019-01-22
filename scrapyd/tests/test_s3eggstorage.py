from twisted.trial import unittest
from mock import MagicMock
from mock import call

from zope.interface.verify import verifyObject

from scrapyd.eggstorages.eggstorage import S3EggStorage

class S3EggStorageTest(unittest.TestCase):
  def setUp(self):
    self.config = MagicMock()
    self.config.get = MagicMock(return_value='eggs')
    self.s3_client = MagicMock()
    self.storage = S3EggStorage(self.config, self.s3_client)

  def test_put(self):
    data = 'data'
    project = 'a'
    version = '1'
    self.s3_client.put_object = MagicMock()

    path = self.storage.put(data, project, version)

    self.failUnlessEqual(path, 'eggs/a/1.egg')
    args, kargs = self.s3_client.put_object.call_args
    self.failUnlessEqual(kargs['Body'], data)
    self.failUnlessEqual(kargs['Bucket'], 'scrapyd-eggs')
    self.failUnlessEqual(kargs['Key'], path)

  def test_get(self):
    data = 'data'
    project = 'a'
    version = '1'
    self.s3_client.get_object = MagicMock(return_value={'Body': data})

    v, egg = self.storage.get(project, version)

    self.failUnlessEqual(egg, data)
    self.failUnlessEqual(v, version)
    args, kargs = self.s3_client.get_object.call_args
    self.failUnlessEqual(kargs['Bucket'], 'scrapyd-eggs')
    self.failUnlessEqual(kargs['Key'], 'eggs/a/1.egg')

  def test_list(self):
    self.s3_client.list_objects = MagicMock(return_value={'Contents': [{'Key': 'eggs/a/2.egg'}, {'Key': 'eggs/a/1.egg'}]})

    result = self.storage.list('a')

    self.failUnlessEqual(result, ['eggs/a/1.egg', 'eggs/a/2.egg'])
    args, kargs = self.s3_client.list_objects.call_args
    self.failUnlessEqual(kargs['Bucket'], 'scrapyd-eggs')
    self.failUnlessEqual(kargs['Prefix'], 'eggs/a')

  def test_delete(self):
    self.s3_client.delete_object = MagicMock()

    self.storage.delete('a', '1')

    args, kargs = self.s3_client.delete_object.call_args
    self.failUnlessEqual(kargs['Bucket'], 'scrapyd-eggs')
    self.failUnlessEqual(kargs['Key'], 'eggs/a/1.egg')

  def test_delete_no_version(self):
    self.s3_client.delete_object = MagicMock()

    self.storage.delete('a')

    args, kargs = self.s3_client.delete_object.call_args
    self.failUnlessEqual(kargs['Bucket'], 'scrapyd-eggs')
    self.failUnlessEqual(kargs['Key'], 'eggs/a')
    
