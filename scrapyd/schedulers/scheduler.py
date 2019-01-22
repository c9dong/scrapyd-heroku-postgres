from zope.interface import Interface
from zope.interface import implementer

from ..utils import get_spider_queues
from ..models.job import Job

class ISpiderScheduler(Interface):

  """A component to schedule spider runs"""

  def schedule(job):
    """Schedule a new job to PENDING state"""


  def run(job):
    """Schedule an existing job to RUNNING state"""


  def finish(job):
    """Schedule an existing job to FINISH state"""


  def list(status=None):
    """List all jobs matching status. If status is None, list all jobs"""


@implementer(ISpiderScheduler)
class SpiderScheduler(object):
  PENDING = 'PENDING'
  RUNNING = 'RUNNING'
  FINISHED = 'FINISHED'

  def __init__(self, db):
    self._db = db
    self._table = 'jobs'

    q = "create table if not exists %s " \
      "(project_name text, " \
      " project_version text, " \
      " spider text, " \
      " job_id text, " \
      " status text, " \
      " priority int default 1, " \
      " updatedAt timestamp without time zone default (now() at time zone 'utc'), " \
      " createdAt timestamp without time zone default (now() at time zone 'utc'));" % self._table
    self._db.execute(q)
    self._db.commit()

  def schedule(self, job):
    q = "insert into %s (project_name, project_version, spider, job_id, status, priority) values (%%s, %%s, %%s, %%s, %%s, %%s)" % self._table
    args = (job.project_name, job.project_version, job.spider, job.job_id, self.PENDING, job.priority)

    self._db.execute(q, args)
    self._db.commit()

  def run(self, job):
    pass

  def finish(self, job):
    pass

  def list(self, status=None):
    q = "select project_name, project_version, spider, job_id, status, priority, updatedAt, createdAt from %s" % self._table
    args = None
    if status is not None:
      q += " where status=%s"
      args = (status,)

    results = self._db.execute(q, args)
    self._db.commit()

    return map(lambda r : self.__result_to_model(r), results)

  def __result_to_model(self, result):
    return Job(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
