# pdnsadm

## Setup

```
docker-compose up --build
```

visit http://localhost:8000 :)

or run django outside docker for easier debugging:

```
docker-compose up --build --scale django=0
export PDNSADM_DEBUG=True
export PDNSADM_SECRET_KEY=secret
export PDNSADM_PDNS_APIURL=http://localhost:8081/api/v1
export PDNSADM_PDNS_APIKEY=pdnsapikey
cd src
./manage.py runserver
```

## Configuration

All config-options are prefixed with `PDNSADM_`.

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
