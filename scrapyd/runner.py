import sys
import os
import shutil
import tempfile
import boto3
from contextlib import contextmanager

from scrapyd import get_application
from scrapyd.eggstorages.eggstorage import S3EggStorage
from scrapyd.eggutils import activate_egg
from scrapyd.config import Config

def get_egg_storage():
    config = Config()
    return S3EggStorage(config, boto3.client('s3'))

@contextmanager
def project_environment(project):
    eggstorage = get_egg_storage()
    eggversion = os.environ.get('SCRAPY_EGG_VERSION', None)
    version, eggfile = eggstorage.get(project, eggversion)
    if eggfile:
        prefix = '%s-%s-' % (project, version)
        fd, eggpath = tempfile.mkstemp(prefix=prefix, suffix='.egg')
        lf = os.fdopen(fd, 'wb')
        shutil.copyfileobj(eggfile, lf)
        lf.close()
        activate_egg(eggpath)
    else:
        eggpath = None
    try:
        assert 'scrapy.conf' not in sys.modules, "Scrapy settings already loaded"
        yield
    finally:
        if eggpath:
            os.remove(eggpath)

def main():
    project = os.environ['SCRAPY_PROJECT']
    with project_environment(project):
        from scrapy.cmdline import execute
        execute()

if __name__ == '__main__':
    main()
