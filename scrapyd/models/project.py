class Project:
  def __init__(self, name, version=None, egg_data=None, path=None, created_at=None):
    self._name = name
    self._version = version
    self._egg_data = egg_data
    self._path = path
    self._created_at = created_at

  @property
  def name(self):
    return self._name

  @property
  def version(self):
    return self._version

  @property
  def egg_data(self):
    return self._egg_data

  @property
  def path(self):
    return self._path

  @property
  def created_at(self):
    return self._created_at

  @property
  def key(self):
    return (self.name, self.version)