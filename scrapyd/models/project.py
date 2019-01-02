class Project:
  def __init__(self, name, version, egg, created_at=None):
    self._name = name
    self._version = version
    self._egg = egg
    self._created_at = created_at

  @property
  def name(self):
    return self._name

  @property
  def version(self):
    return self._version

  @property
  def egg(self):
    return self._egg

  @property
  def created_at(self):
    return self._created_at

  @property
  def key(self):
    return (self.name, self.version)