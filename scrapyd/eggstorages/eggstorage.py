import re
from glob import glob
from os import path, makedirs, remove
from shutil import copyfileobj, rmtree
from distutils.version import LooseVersion
from zope.interface import Interface
from zope.interface import implementer

class IEggStorage(Interface):
  """A component that handles storing and retrieving eggs"""

  def put(eggfile, project, version):
    """Store the egg (passed in the file object) under the given project and
    version"""

  def get(project, version):
    """Return a tuple (version, file) with the the egg for the specified
    project and version. If version is None, the latest version is
    returned. If no egg is found for the given project/version (None, None)
    should be returned."""

  def list(project):
    """Return the list of versions which have eggs stored (for the given
    project) in order (the latest version is the currently used)."""

  def delete(project, version=None):
    """Delete the egg stored for the given project and version. If should
    also delete the project if no versions are left"""

@implementer(IEggStorage)
class S3EggStorage(object):
  def __init__(self, config, s3_client):
    self._basedir = config.get('eggs_dir', 'eggs')
    self._config = config
    self._s3_client = s3_client
    self._bucket_name = 'scrapyd-eggs'
    self.__create_bucket()

  def __create_bucket(self):
    buckets = self._s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in buckets['Buckets']]
    for b in buckets:
      if b == self._bucket_name:
        return
    self._s3_client.create_bucket(Bucket=self._bucket_name)

  def put(self, egg_data, project, version):
    eggpath = self._eggpath(project, version)
    self._s3_client.put_object(Body=egg_data, Bucket=self._bucket_name, Key=eggpath)
    return eggpath

  def get(self, project, version):
    eggpath = self._eggpath(project, version)
    egg = self._s3_client.get_object(Bucket=self._bucket_name, Key=eggpath)['Body']
    return version, egg

  def list(self, project):
    eggdir = path.join(self._basedir, project)
    eggs = self._s3_client.list_objects(Bucket=self._bucket_name, Prefix=eggdir)['Contents']
    return sorted([c['Key'] for c in eggs])

  def delete(self, project, version=None):
    if version is None:
      path = path.join(self._basedir, project)
    else:
      path = self._eggpath(project, version)

    self._s3_client.delete_object(Bucket=self._bucket_name, Key=path)


  def _eggpath(self, project, version):
    sanitized_version = re.sub(r'[^a-zA-Z0-9_-]', '_', version)
    x = path.join(self._basedir, project, "%s.egg" % sanitized_version)
    return x

@implementer(IEggStorage)
class FilesystemEggStorage(object):

  def __init__(self, config):
    self.basedir = config.get('eggs_dir', 'eggs')

  def put(self, egg_data, project, version):
    eggpath = self._eggpath(project, version)
    eggdir = path.dirname(eggpath)
    if not path.exists(eggdir):
      makedirs(eggdir)
    with open(eggpath, 'wb') as f:
      f.write(egg_data)

  def get(self, project, version):
    if version is None:
      try:
        version = self.list(project)[-1]
      except IndexError:
        return None, None
    return version, open(self._eggpath(project, version), 'rb')

  def list(self, project):
    eggdir = path.join(self.basedir, project)
    versions = [path.splitext(path.basename(x))[0] \
      for x in glob("%s/*.egg" % eggdir)]
    return sorted(versions, key=LooseVersion)

  def delete(self, project, version=None):
    if version is None:
      rmtree(path.join(self.basedir, project))
    else:
      remove(self._eggpath(project, version))
      if not self.list(project): # remove project if no versions left
        self.delete(project)

  def _eggpath(self, project, version):
    sanitized_version = re.sub(r'[^a-zA-Z0-9_-]', '_', version)
    x = path.join(self.basedir, project, "%s.egg" % sanitized_version)
    return x
