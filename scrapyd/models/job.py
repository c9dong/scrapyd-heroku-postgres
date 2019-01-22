from project import Project

class Job:
  def __init__(self, project_name, project_version, spider, job_id=None, status=None, priority=None, updated_at=None, created_at=None):
    self._project_name = project_name
    self._project_version = project_version
    self._spider = spider
    self._job_id = job_id
    self._status = status
    self._priority = priority
    self._updated_at = updated_at
    self._created_at = created_at

  @property
  def project_name(self):
    return self._project_name

  @property
  def project_version(self):
    return self._project_version

  @property
  def project(self):
    return Project(self.project_name, self.project_version)

  @property
  def spider(self):
    return self._spider

  @property
  def job_id(self):
    return self._job_id

  @property
  def status(self):
    return self._status

  @property
  def priority(self):
    return self._priority

  @property
  def updated_at(self):
    return self._updated_at

  @property
  def created_at(self):
    return self._created_at