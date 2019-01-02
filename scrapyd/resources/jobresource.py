from wsresource import WsResource

class JobResource(WsResource):
  '''
  schedule a new job
  '''
  def render_POST(self, txrequest):
    txrequest.setResponseCode(501)
    return None

  '''
  cancel an existing job
  '''
  def render_DELETE(self, txrequest):
    txrequest.setResponseCode(501)
    return None

  '''
  list all jobs
  '''
  def render_GETALL(self, txrequest):
    txrequest.setResponseCode(501)
    return None