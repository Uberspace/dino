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
    :target: https://dino.readthedocs.io/
    
.. |python| image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :alt: Python 3.6+
    :scale: 100%

a modern DNS record editor for PowerDNS. It uses the PowerDNS-API, has a high
test coverage, rich documentation and comes with batteries included!

Development
-----------

The following instructions are for development setups only. Refer to the
documentation linked above on how to get a production setup up and running.

Setup
^^^^^

Start a PowerDNS server, mysql (for PowerDNS only) and dino inside docker:

.. code-block:: text

    docker-compose up --build

... then visit http://localhost:8000 :)

If you prefer to run django locally for easier debugging, you can skip it in the
docker setup, like so:

.. code-block:: text

    docker-compose up --build --scale django=0
    export DINO_DEBUG=True
    export DINO_SECRET_KEY=secret
    export DINO_PDNS_APIURL=http://localhost:8081/api/v1
    export DINO_PDNS_APIKEY=pdnsapikey
    cd src
    ./manage.py runserver

... then, again, visit http://localhost:8000 :)

Tests
^^^^^

Run all tests including the linter, like they would be run in CI:

.. code-block:: text

    $ tox
    GLOB sdist-make: /home/luto/uberspace/dino/src/setup.py
    lint recreate: /home/luto/uberspace/dino/.env
    (...)
    lint: commands succeeded
    test-py36: commands succeeded
    test-py37: commands succeeded
    congratulations :)

Takes too long? Run ``tox --listenvs`` to get a list of tasks, run them
individually using ``tox -e $ENV``:

.. code-block:: text

    $ tox -e lint
    GLOB sdist-make: /home/luto/uberspace/dino/src/setup.py
    lint recreate: /home/luto/uberspace/dino/.env
    (...)
    lint: commands succeeded
    congratulations :)

Acknowledgements
----------------

Some meta configuration like :code:`setup.py` and :code:`setup.cfg` has been lifted from the
awesome conference management system pretalx (MIT). Thanks!
