from wsresource import WsResource

class ProjectResource(WsResource):
  '''
  add a new version of a project
  '''
  def render_POST(self, txrequest):
    txrequest.setResponseCode(501)
    return None

  '''
  remove a project, or a specific version
  '''
  def render_DELETE(self, txrequest):
    txrequest.setResponseCode(501)
    return None

  '''
  list all projects, or all versions of a particular project
  '''
  def render_GETALL(self, txrequest):
    txrequest.setResponseCode(501)
    return None