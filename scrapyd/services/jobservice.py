import uuid
from os import environ

from spiderservice import SpiderServiceFactory
from ..schedulers.scheduler import SpiderScheduler
from ..db.pgdbadapter import PgDbAdapter

class JobService:
  def __init__(self, spider_service, scheduler):
    self._spider_service = spider_service
    self._scheduler = scheduler

  def post(self, job):
    spiders = self._spider_service.getall(job.project)
    if not job.spider in spiders:
      raise Exception('spider not found')
    
    job._job_id = uuid.uuid1().hex
    job._priority = 1

    self._scheduler.schedule(job)

    return job._job_id


  def delete(self):
    pass

  def getall(self, status=None):
    return self._scheduler.list(status)

class JobServiceFactory:
  obj = None

  @classmethod
  def build(cls):
    if cls.obj is None:
      spider_service = SpiderServiceFactory.build()
      database = environ.get('DATABASE_URL')
      db = PgDbAdapter(database)
      scheduler = SpiderScheduler(db)
      cls.obj = JobService(spider_service, scheduler)

    return cls.obj