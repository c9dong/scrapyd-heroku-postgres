from wsresource import WsResource

class DaemonResource(WsResource):
  '''
  get the daemon status
  '''
  def render_GET(self, txrequest):
    txrequest.setResponseCode(501)
    return None