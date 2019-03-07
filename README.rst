dino
====

|build-status| |coverage| |docs| |python|

.. |build-status| image:: https://travis-ci.com/Uberspace/dino.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.com/Uberspace/dino
    
.. |coverage| image:: https://codecov.io/gh/Uberspace/dino/branch/master/graph/badge.svg
    :alt: Coverage
    :scale: 100%
    :target: https://codecov.io/gh/Uberspace/dino
    
.. |docs| image:: https://readthedocs.org/projects/dino/badge/?version=latest
    :alt: Documentation
    :scale: 100%
    :target: https://dino.readthedocs.io/en/latest/?badge=latest
    
.. |python| image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :alt: Python 3.6+
    :scale: 100%


Setup
-----

.. code-block:: text

    docker-compose up --build
  
visit http://localhost:8000 :)

or run django outside docker for easier debugging:

.. code-block:: text

    docker-compose up --build --scale django=0
    export DINO_DEBUG=True
    export DINO_SECRET_KEY=secret
    export DINO_PDNS_APIURL=http://localhost:8081/api/v1
    export DINO_PDNS_APIKEY=pdnsapikey
    cd src
    ./manage.py runserver

Configuration
-------------

All config-options are prefixed with :code:`DINO_`.

Django Settings
...............

* :code:`SECRET_KEY`
* :code:`DEBUG`
* :code:`ALLOWED_HOSTS`

See the `django configuration`_ for details.

.. _django configuration: https://docs.djangoproject.com/en/2.1/ref/settings/

Other Settings
..............

* :code:`PDNS_APIKEY`: powerdns API key, see `pdns documentation`_.
* :code:`PDNS_APIURL`
* :code:`DB_URL`: database configuration, as `a single URL`_.
* :code:`CUSTOM_RECORD_TYPES`: comma seperated list of addition record types (e.g. :code:`NSEC,NSEC3,NSEC3PARAM`)
* :code:`ENABLE_SIGNUP`: set to :code:`True` to enable public registration
* :code:`ZONE_DEFAULT_KIND`: the `powerdns zone kind`_, may be :code:`Native`, :code:`Master` or :code:`Slave`
* :code:`ZONE_DEFAULT_NAMESERVERS`: comma separated list of nameservers to use for new zones

.. _pdns documentation: https://doc.powerdns.com/authoritative/http-api/index.html#enabling-the-api
.. _a single URL: https://github.com/kennethreitz/dj-database-url#url-schema
.. _powerdns zone kind: https://doc.powerdns.com/authoritative/http-api/zone.html#zone

Acknowledgements
----------------

Some meta configuration like :code:`setup.py` and :code:`setup.cfg` has been lifted from the
awesome conference management system pretalx (MIT). Thanks!