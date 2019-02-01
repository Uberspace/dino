import os

os.environ['DINO_SECRET_KEY'] = 'secret'
os.environ['DINO_PDNS_APIKEY'] = ''
os.environ['DINO_PDNS_APIURL'] = 'http://example.org'

from .settings import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['*']
