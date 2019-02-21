# dino
[![Build Status](https://travis-ci.com/Uberspace/dino.svg?branch=master)](https://travis-ci.com/Uberspace/dino)
[![Coverage](https://codecov.io/gh/Uberspace/dino/branch/master/graph/badge.svg)](https://codecov.io/gh/Uberspace/dino)
[![Documentation](https://readthedocs.org/projects/dino/badge/?version=latest)](https://dino.readthedocs.io/en/latest/?badge=latest)

## Setup

```
docker-compose up --build
```

visit http://localhost:8000 :)

or run django outside docker for easier debugging:

```
docker-compose up --build --scale django=0
export DINO_DEBUG=True
export DINO_SECRET_KEY=secret
export DINO_PDNS_APIURL=http://localhost:8081/api/v1
export DINO_PDNS_APIKEY=pdnsapikey
cd src
./manage.py runserver
```

## Configuration

All config-options are prefixed with `DINO_`.

### Django Settings

* `SECRET_KEY`
* `DEBUG`
* `ALLOWED_HOSTS`

See the [django configuration](https://docs.djangoproject.com/en/2.1/ref/settings/)
for details.

### Other Settings

* `PDNS_APIKEY`: powerdns API key, see [pdns documentation](https://doc.powerdns.com/authoritative/http-api/index.html#enabling-the-api).
* `PDNS_APIURL`
* `DB_URL`: database configuration, as [a single URL](https://github.com/kennethreitz/dj-database-url#url-schema).
* `CUSTOM_RECORD_TYPES`: comma seperated list of addition record types (e.g. `NSEC,NSEC3,NSEC3PARAM`)
* `ENABLE_SIGNUP`: set to `True` to enable public registration
* `ZONE_DEFAULT_KIND`: the [powerdns zone kind](https://doc.powerdns.com/authoritative/http-api/zone.html#zone), may be `Native`, `Master` or `Slave`
* `ZONE_DEFAULT_NAMESERVERS`: comma seperated list of nameservers to use for new zones

## Acknowledgements

Some meta configuration like `setup.py` and `setup.cfg` has been lifted from the
awesome conference management system [pretalx](https://github.com/pretalx/pretalx)
(MIT). Thanks!
