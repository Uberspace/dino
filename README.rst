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

a modern DNS record editor for PowerDNS. It uses the PowerDNS-API, has a high
test coverage, rich documentation and comes with batteries included!


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

Acknowledgements
----------------

Some meta configuration like :code:`setup.py` and :code:`setup.cfg` has been lifted from the
awesome conference management system pretalx (MIT). Thanks!
