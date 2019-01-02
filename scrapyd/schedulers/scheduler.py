from zope.interface import Interface
from zope.interface import implementer

from ..utils import get_spider_queues

class ISpiderScheduler(Interface):
  """A component to schedule spider runs"""

  def schedule(project, spider_name, **spider_args):
    """Schedule a spider for the given project"""

  def list_projects():
    """Return the list of available projects"""

  def update_projects():
    """Called when projects may have changed, to refresh the available
    projects"""


@implementer(ISpiderScheduler)
class SpiderScheduler(object):
  def __init__(self, config):
    self.config = config
    self.queues = {}
    self.update_projects()

  def schedule(self, project, spider_name, **spider_args):
    q = self.queues[project]
    q.add(spider_name, **spider_args)

  def list_projects(self):
    return self.queues.keys()

  def update_projects(self):
    self.queues = get_spider_queues(self.config)
