from wsresource import WsResource
from ..services.jobservice import JobServiceFactory
from ..models.job import Job

class JobResource(WsResource):
  def __init__(self, root):
    WsResource.__init__(self, root)
    self._service = JobServiceFactory.build()

  '''
  schedule a new job
  -- curl "http://127.0.0.1:6800/jobs?name=abc&version=1&spider=spider2" -X POST
  '''
  def render_POST(self, txrequest):
    name = txrequest.args[b'name'][0].decode('utf-8')
    version = txrequest.args[b'version'][0].decode('utf-8')
    spider = txrequest.args[b'spider'][0].decode('utf-8')

    job = Job(name, version, spider)

    job_id = self._service.post(job)

    return {'job_id': job_id}


  '''
  cancel an existing job
  '''
  def render_DELETE(self, txrequest):
    txrequest.setResponseCode(501)
    return None

  '''
  list all jobs
  -- curl "http://127.0.0.1:6800/jobs?name=abc&version=1&spider=spider1" -X GETALL
  '''
  def render_GETALL(self, txrequest):
    status = None
    if b'status' in txrequest.args:
      status = txrequest.args[b'status'][0].decode('utf-8')

    data = self._service.getall(status)
    return map(lambda p : self.__to_json(p), data)


  def __to_json(self, job):
    return {
      'name': job.project_name,
      'version': job.project_version,
      'spider': job.spider,
      'job_id': job.job_id,
      'status': job.status,
      'priority': job.priority,
      'updated_at': int(job.updated_at.strftime("%s")) * 1000,
      'created_at': int(job.created_at.strftime("%s")) * 1000
    }