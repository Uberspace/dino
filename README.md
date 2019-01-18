# pdnsadm

## Setup

```
docker-compose up --build
```

visit http://localhost:8080 :)

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
* `DB_URL`: database configuration, as [a single URL](https://github.com/kennethreitz/dj-database-url#url-schema).
