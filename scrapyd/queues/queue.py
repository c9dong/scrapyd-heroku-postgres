from zope.interface import Interface
from zope.interface import implementer

class ISpiderQueue(Interface):

  def add(name, **spider_args):
    """Add a spider to the queue given its name a some spider arguments.

    This method can return a deferred. """

  def pop():
    """Pop the next mesasge from the queue. The messages is a dict
    conaining a key 'name' with the spider name and other keys as spider
    attributes.

    This method can return a deferred. """

  def list():
    """Return a list with the messages in the queue. Each message is a dict
    which must have a 'name' key (with the spider name), and other optional
    keys that will be used as spider arguments, to create the spider.

    This method can return a deferred. """

  def count():
    """Return the number of spiders in the queue.

    This method can return a deferred. """

  def remove(func):
    """Remove all elements from the queue for which func(element) is true,
    and return the number of removed elements.
    """

  def clear():
    """Clear the queue.

    This method can return a deferred. """


@implementer(ISpiderQueue)
class SpiderQueue(object):

  def __init__(self, dbqueue):
    self._q = dbqueue

  def add(self, name, **spider_args):
    d = spider_args.copy()
    d['name'] = name
    priority = float(d.pop('priority', 0))
    self._q.put(d, priority)

  def pop(self):
    return self._q.pop()

  def count(self):
    return len(self._q)

  def list(self):
    return [x[0] for x in self._q]

  def remove(self, func):
    return self._q.remove(func)

  def clear(self):
    self._q.clear()
