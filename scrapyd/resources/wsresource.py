from .jsonresource import JsonResource

class WsResource(JsonResource):

  def __init__(self, root):
    JsonResource.__init__(self)
    self.root = root

    def render(self, txrequest):
      try:
        return JsonResource.render(self, txrequest).encode('utf-8')
      except Exception as e:
        if self.root.debug:
          return traceback.format_exc().encode('utf-8')
        log.err()
        r = {"node_name": self.root.nodename, "status": "error", "message": str(e)}
        return self.render_object(r, txrequest).encode('utf-8')