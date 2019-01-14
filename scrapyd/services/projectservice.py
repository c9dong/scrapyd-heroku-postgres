import os
from os import environ

from ..db.pgdbadapter import PgDbAdapter
from ..models.project import Project
from ..eggstorages.eggstorage import FilesystemEggStorage
from ..config import Config

class ProjectService:
  def __init__(self, db, egg_storage):
    self._db = db
    self._egg_storage = egg_storage
    self._table = 'projects'
    self._project_dir = '_projects'

    q = "create table if not exists %s " \
      "(name text, " \
      " version text, " \
      " createdAt timestamp without time zone default (now() at time zone 'utc'));" % self._table
    self._db.execute(q)
    self._db.commit()

  def post(self, project):
    if len(self.__get(project.key)) > 0:
      return

    q = "insert into %s (name, version) values (%%s,%%s)" % self._table
    args = (project.name, project.version)

    self._db.execute(q, args)
    self._db.commit()

    self._egg_storage.put(project.egg_data, project.name, project.version)

  def delete(self, name, version=None):
    q = "delete from %s where name=%%s" % self._table
    args = (name,)
    if version is not None:
      q += " and version=%s"
      args = (name, version)

    self._db.execute(q, args)
    self._db.commit()

    self._egg_storage.delete(name, version)


  def get(self, name, version=None):
    project = Project(name, version)
    results = self.__get(project.key)

    return map(lambda r : self.__result_to_model(r), results)

  def getall(self):
    q = "select a.name, a.version, a.createdAt from " \
      " ( select name, max(createdAt) as maxTime " \
          " from %s " \
          " group by name) gb " \
      " inner join %s a " \
      " on a.name = gb.name and a.createdAt = gb.maxTime" % (self._table, self._table)

    results = self._db.execute(q)
    self._db.commit()

    return map(lambda r : self.__result_to_model(r), results)

  def __result_to_model(self, result):
    return Project(result[0], result[1], '', result[2])

  def __get(self, project_key):
    q = "select name, version, createdAt from %s where name=%%s" % self._table
    args = (project_key[0],)
    if project_key[1] is not None:
      q += " and version=%s"
      args = (project_key[0], project_key[1])

    results = self._db.execute(q, args)
    self._db.commit()

    return results
    

class ProjectServiceFactory:
  @classmethod
  def build(cls):
    database = environ.get('DATABASE_URL')
    db = PgDbAdapter(database)
    egg_storage = FilesystemEggStorage(Config())
    return ProjectService(db, egg_storage)