from zope.interface import implementer
from zope.interface import Interface
from six import iteritems
from twisted.internet.defer import DeferredQueue, inlineCallbacks, maybeDeferred, returnValue

from ..utils import get_spider_queues

class IPoller(Interface):
  """A component that polls for projects that need to run"""

  def poll():
    """Called periodically to poll for projects"""

  def next():
    """Return the next message.

    It should return a Deferred which will get fired when there is a new
    project that needs to run, or already fired if there was a project
    waiting to run already.

    The message is a dict containing (at least):
    * the name of the project to be run in the '_project' key
    * the name of the spider to be run in the '_spider' key
    * a unique identifier for this run in the `_job` key
    This message will be passed later to IEnvironment.get_environment().
    """

  def update_projects():
    """Called when projects may have changed, to refresh the available
    projects"""


@implementer(IPoller)
class QueuePoller(object):

  def __init__(self, config):
    self.config = config
    self.update_projects()
    self.dq = DeferredQueue(size=1)

  @inlineCallbacks
  def poll(self):
    if self.dq.pending:
      return
    for p, q in iteritems(self.queues):
      c = yield maybeDeferred(q.count)
      if c:
        msg = yield maybeDeferred(q.pop)
        if msg is not None:  # In case of a concurrently accessed queue
          returnValue(self.dq.put(self._message(msg, p)))

  def next(self):
    return self.dq.get()

  def update_projects(self):
    self.queues = get_spider_queues(self.config)

  def _message(self, queue_msg, project):
    d = queue_msg.copy()
    d['_project'] = project
    d['_spider'] = d.pop('name')
    return d
