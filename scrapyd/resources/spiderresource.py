from wsresource import WsResource

class SpiderResource(WsResource):
  '''
  get all spiders in a project
  '''
  def render_GETALL(self, txrequest):
    txrequest.setResponseCode(501)
    return None