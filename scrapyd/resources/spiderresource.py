from wsresource import WsResource
from ..models.project import Project
from ..services.spiderservice import SpiderServiceFactory

class SpiderResource(WsResource):
  def __init__(self, root):
    WsResource.__init__(self, root)
    self._service = SpiderServiceFactory.build()

  '''
  get all spiders in a project
  -- curl "http://127.0.0.1:6800/spiders?name=abc&version=1" -X GETALL
  '''
  def render_GETALL(self, txrequest):
    name = txrequest.args[b'name'][0].decode('utf-8')
    version = txrequest.args[b'version'][0].decode('utf-8')
    project = Project(name, version)

    spiders = self._service.getall(project)
    return {'project': name, 'version': version, 'spiders': spiders}