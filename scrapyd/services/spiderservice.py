import os
import sys
import subprocess
import six

from ..models.project import Project
from ..exceptions.httpexception import HttpException, HTTP_404_NOT_FOUND
from ..utils import UtilsCache

class SpiderService:
  def __init__(self, spider_cache, subprocess_):
    self._cache = spider_cache
    self._subprocess = subprocess_

  def getall(self, project):
    return self.get_spider_list(project.name, runner='scrapyd.runner', version=project.version)


  def get_spider_list(self, project, runner, pythonpath=None, version=''):
    """Return the spider list from the given project, using the given runner"""
    try:
      return self._cache[project][version]
    except KeyError:
      pass
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'UTF-8'
    env['SCRAPY_PROJECT'] = project
    if pythonpath:
      env['PYTHONPATH'] = pythonpath
    if version:
      env['SCRAPY_EGG_VERSION'] = version
    pargs = [sys.executable, '-m', runner, 'list']
    proc = self._subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

    out, err = proc.communicate()
    if proc.returncode:
      msg = err or out or ''
      msg = msg.decode('utf8')
      raise RuntimeError(msg.encode('unicode_escape') if six.PY2 else msg)
    # FIXME: can we reliably decode as UTF-8?
    # scrapy list does `print(list)`
    tmp = out.decode('utf-8').splitlines()
    try:
      project_cache = self._cache[project]
      project_cache[version] = tmp
    except KeyError:
      project_cache = {version: tmp}
    self._cache[project] = project_cache
    return tmp

class SpiderServiceFactory:
  @classmethod
  def build(cls):
    return SpiderService(UtilsCache(), subprocess)