from os import environ

from ..db.pgdbadapter import PgDbAdapter
from ..models.project import Project

class ProjectService:
  def __init__(self, db):
    self._db = db
    self._table = 'projects'

    q = "create table if not exists %s " \
      "(name text, " \
      " version text, " \
      " egg text, " \
      " createdAt timestamp without time zone default (now() at time zone 'utc'));" % self._table
    self._db.execute(q)
    self._db.commit()

  def post(self, project):
    q = "insert into %s (name, version, egg) values (%%s,%%s,%%s)" % self._table
    args = (project.name, project.version, project.egg)

    self._db.execute(q, args)
    self._db.commit()

  def delete(self, name, version=None):
    q = "delete from %s where name=%%s" % self._table
    args = (name,)
    if version is not None:
      q += " and version=%%s"
      args = (name, version)

    self._db.execute(q, args)
    self._db.commit()

  def get(self, name, version=None):
    q = "select name, version, egg, createdAt from %s where name=%%s" % self._table
    args = (name,)
    if version is not None:
      q += " and version=%%s"
      args = (name, version)

    results = self._db.execute(q, args)
    self._db.commit()

    return map(lambda r : self.__result_to_model(r), results)

  def getall(self):
    q = "select a.name, a.version, a.egg, a.createdAt from " \
      " ( select name, max(createdAt) as maxTime " \
          " from %s " \
          " group by name) gb " \
      " inner join %s a " \
      " on a.name = gb.name and a.createdAt = gb.maxTime" % (self._table, self._table)

    results = self._db.execute(q)
    self._db.commit()

    return map(lambda r : self.__result_to_model(r), results)

  def __result_to_model(self, result):
    return Project(result[0], result[1], result[2], result[3])
    

class ProjectServiceFactory:
  @classmethod
  def build(cls):
    database = environ.get('DATABASE_URL')
    db = PgDbAdapter(database)
    return ProjectService(db)