import os

os.environ['DINO_SECRET_KEY'] = 'secret'
os.environ['DINO_PDNS_APIKEY'] = ''
os.environ['DINO_PDNS_APIURL'] = 'http://example.org'
os.environ['DINO_ALLOWED_HOSTS'] = '*'
os.environ['DINO_DEBUG'] = 'False'

from .settings import *  # noqa
