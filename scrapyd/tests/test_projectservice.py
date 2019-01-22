from twisted.trial import unittest
from mock import MagicMock
from mock import call

from zope.interface.verify import verifyObject

from scrapyd.services.projectservice import ProjectService
from scrapyd.models.project import Project

class ProjectServiceTest(unittest.TestCase):
  def setUp(self):
    self.db = MagicMock()
    self.db.execute = MagicMock()
    self.db.commit = MagicMock()
    self.egg_store = MagicMock()
    self.service = ProjectService(self.db, self.egg_store)

  def test_get(self):
    name = 'name'
    mock_data = [(name, '1', '/name/1', 1234), (name, '2', '/name/2', 1235)]
    self.db.execute = MagicMock(return_value=mock_data)
    data = self.service.get(name)

    self.db.execute.assert_called_with('select name, version, path, createdAt from projects where name=%s', (name,))
    self.db.commit.assert_called_with()

    self.failUnlessEqual(len(data), 2)
    self.__assert_project(data[0], mock_data[0])
    self.__assert_project(data[1], mock_data[1])

  def test_get_version(self):
    name = 'name'
    version = '1'
    mock_data = [(name, version, '/name/1', 1234)]
    self.db.execute = MagicMock(return_value=mock_data)
    data = self.service.get(name, version)

    self.db.execute.assert_called_with('select name, version, path, createdAt from projects where name=%s and version=%s', (name,version))
    self.db.commit.assert_called_with()

    self.failUnlessEqual(len(data), 1)
    self.__assert_project(data[0], mock_data[0])

  def test_getall(self):
    mock_data = [('a', '1', '/a/1', 1234), ('b', '1', '/b/1', 1235)]
    self.db.execute = MagicMock(return_value=mock_data)
    data = self.service.getall()

    self.db.execute.assert_called_with('select a.name, a.version, a.path, a.createdAt from  ( select name, max(createdAt) as maxTime  from projects  group by name) gb  inner join projects a  on a.name = gb.name and a.createdAt = gb.maxTime')
    self.db.commit.assert_called_with()

    self.failUnlessEqual(len(data), 2)
    self.__assert_project(data[0], mock_data[0])
    self.__assert_project(data[1], mock_data[1])

  def test_post(self):
    post_project = Project('a', '1', 'data', 'path', 1234)
    self.egg_store.put = MagicMock(return_value='path')
    self.db.execute = MagicMock()
    self.db.execute.side_effect = [[], None]

    self.service.post(post_project)

    calls = [call('select name, version, path, createdAt from projects where name=%s and version=%s', ('a', '1')), call('insert into projects (name, version, path) values (%s,%s, %s)', ('a', '1', 'path'))]
    self.db.execute.assert_has_calls(calls, any_order=True)
    self.db.commit.assert_has_calls([call(), call()])
    self.egg_store.put.assert_called_with('data', 'a', '1')

  def test_post_exist(self):
    post_project = Project('a', '1', 'data', 'path', 1234)
    self.egg_store.put = MagicMock(return_value='path')
    self.db.execute = MagicMock()
    self.db.execute.side_effect = [[Project('a', '1')], None]

    self.service.post(post_project)

    calls = [call('select name, version, path, createdAt from projects where name=%s and version=%s', ('a', '1'))]
    self.db.execute.assert_has_calls(calls, any_order=True)
    self.db.commit.assert_has_calls([call()])
    self.egg_store.put.assert_not_called()


  def test_delete(self):
    name = 'name'
    self.db.execute = MagicMock()
    self.egg_store.delete = MagicMock()

    data = self.service.delete(name)

    self.db.execute.assert_called_with('delete from projects where name=%s', (name,))
    self.db.commit.assert_called_with()
    self.egg_store.delete.assert_called_with(name, None)

  def test_delete_version(self):
    name = 'name'
    version = '1'
    self.db.execute = MagicMock()
    self.egg_store.delete = MagicMock()

    data = self.service.delete(name, version)

    self.db.execute.assert_called_with('delete from projects where name=%s and version=%s', (name, version))
    self.db.commit.assert_called_with()
    self.egg_store.delete.assert_called_with(name, version)

  def __assert_project(self, project, args):
    self.failUnlessEqual(args[0], project.name)
    self.failUnlessEqual(args[1], project.version)
    self.failUnlessEqual(args[2], project.path)
    self.failUnlessEqual(args[3], project.created_at)
