from wsresource import WsResource
from ..services.projectservice import ProjectServiceFactory
from ..models.project import Project

class ProjectResource(WsResource):
  def __init__(self, root):
    WsResource.__init__(self, root)
    self._service = ProjectServiceFactory.build()

  '''
  add a new version of a project
  -- curl "http://127.0.0.1:6800/projects?name=abc&version=1" -X POST --data-binary @scrapyd/tests/mybot.egg
  '''
  def render_POST(self, txrequest):
    name = txrequest.args[b'name'][0].decode('utf-8')
    version = txrequest.args[b'version'][0].decode('utf-8')

    egg_data = txrequest.content.read()

    project = Project(name, version, egg_data)

    self._service.post(project)

  '''
  remove a project, or a specific version
  -- curl "http://127.0.0.1:6800/projects?name=abc&version=2" -X DELETE
  -- curl "http://127.0.0.1:6800/projects?name=abc" -X DELETE
  '''
  def render_DELETE(self, txrequest):
    name = txrequest.args[b'name'][0].decode('utf-8')
    version = None
    if b'version' in txrequest.args:
      version = txrequest.args[b'version'][0].decode('utf-8')

    self._service.delete(name, version)

  '''
  list a project, or a specific version of a project
  -- curl "http://127.0.0.1:6800/projects?name=abc&version=1"
  -- curl "http://127.0.0.1:6800/projects?name=abc"
  '''
  def render_GET(self, txrequest):
    name = txrequest.args[b'name'][0].decode('utf-8')
    version = None
    if b'version' in txrequest.args:
      version = txrequest.args[b'version'][0].decode('utf-8')
      print version
    
    data = self._service.get(name, version)
    return map(lambda p : self.__to_json(p), data)

  '''
  list the latest version of all projects
  -- curl "http://127.0.0.1:6800/projects" -X GETALL
  '''
  def render_GETALL(self, txrequest):
    data = self._service.getall()
    return map(lambda p : self.__to_json(p), data)

  def __to_json(self, project):
    return {
      'name': project.name,
      'version': project.version,
      'path': project.path,
      'createdAt': int(project.created_at.strftime("%s")) * 1000
    }