from os import environ

from twisted.application.service import Application
from twisted.application.internet import TimerService, TCPServer
from twisted.web import server
from twisted.python import log

from scrapy.utils.misc import load_object

from .eggstorages.eggstorage import IEggStorage
from .eggstorages.eggstorage import FilesystemEggStorage
from .environments.environment import IEnvironment
from .environments.environment import Environment
from .pollers.poller import IPoller
from .pollers.poller import QueuePoller
from .schedulers.scheduler import ISpiderScheduler
from .schedulers.scheduler import SpiderScheduler

from .config import Config

def application(config):
    app = Application("Scrapyd")
    http_port = config.getint('http_port', 6800)
    bind_address = config.get('bind_address', '127.0.0.1')
    poll_interval = config.getfloat('poll_interval', 5)
    database = environ.get('DATABASE_URL')

    poller = QueuePoller(config)
    eggstorage = FilesystemEggStorage(config)
    scheduler = SpiderScheduler(config)
    environment = Environment(config)

    app.setComponent(IPoller, poller)
    app.setComponent(IEggStorage, eggstorage)
    app.setComponent(ISpiderScheduler, scheduler)
    app.setComponent(IEnvironment, environment)

    laupath = config.get('launcher', 'scrapyd.launcher.Launcher')
    laucls = load_object(laupath)
    launcher = laucls(config, app)

    webpath = config.get('webroot', 'scrapyd.website.Root')
    webcls = load_object(webpath)

    timer = TimerService(poll_interval, poller.poll)
    webservice = TCPServer(http_port, server.Site(webcls(config, app)), interface=bind_address)
    log.msg(format="Scrapyd web console available at http://%(bind_address)s:%(http_port)s/",
            bind_address=bind_address, http_port=http_port)

    launcher.setServiceParent(app)
    timer.setServiceParent(app)
    webservice.setServiceParent(app)

    return app
