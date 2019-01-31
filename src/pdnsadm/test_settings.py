import os

os.environ['PDNSADM_SECRET_KEY'] = 'secret'
os.environ['PDNSADM_PDNS_APIKEY'] = ''
os.environ['PDNSADM_PDNS_APIURL'] = 'http://example.org'

from .settings import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['*']
