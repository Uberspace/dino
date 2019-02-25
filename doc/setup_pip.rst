Setup using pip
===============

This guide explains how to install dino inside a fresh ubuntu 18.04 bionic box.
It includes the installation of all on-host prerequisites and provides you with
a fully functional Dino instance.

Most of the steps are the same for other distributions like Debian or CentOS, so
you should be able to adpat this to your needs as you go. We'd be glad about
full guides for other operating systems. So please feel free to send us tips or
even open a `Pull Request <https://github.com/Uberspace/dino/>`_ on GitHub.

Prerequisites
-------------

PowerDNS
^^^^^^^^

To use dino, a running PowerDNS instance is required. In addition to the default
config, the following options are needed:

.. code-block:: ini

  # 1. enable the API and choose a sane API key
  api=yes
  api-key=SOME_LONG_API_KEY_CHANGE_ME_PLEASE

  # 2. enable the webserver and give dino acces to it
  #    either by whitelisting it here, in your reverse proxy or in your firewall.
  webserver=yes
  webserver-address=0.0.0.0
  webserver-port=8080
  webserver-allow-from=1.2.3.4/32

Remember (... or write down) server hostname, webserver port as well as
the API key.

Python 3.6
^^^^^^^^^^

Python 3.6 or newer is required. Ubuntu already comes with python 3.6, so we're
good here. To complete the our python setup, install the package manager pip,
which is needed later.

.. code-block:: console

  root@ubuntu-bionic:~# python3 --version
  Python 3.6.7
  root@ubuntu-bionic:~# apt install -y python3-pip
  Reading package lists... Done
  Building dependency tree       
  Reading state information... Done
  The following additional packages will be installed:
  (...)

.. note::
  **Debian** users might be able to compile python 3.6 from source or get it
  from the `Debian Sid repos <https://packages.debian.org/sid/python3.6>`_.

.. note::
  **CentOS** users can get python 3.6 from the `IUS Project <https://ius.io>`_;
  install ``python36u`` as well as ``python36u-pip``.

uWSGI
^^^^^

uWSGI actually runs dino will later provide it via HTTP on port 8080. It is
installed globally using pythons dependency manager ``pip``:

.. code-block:: console
 
  root@ubuntu-bionic:~# pip3 install uwsgi
  Collecting uwsgi
    Downloading https://files.py..
  (...)

System User
^^^^^^^^^^^

To make sure dino can only access what it needs to access, create a new user.

.. note::

  Instead of using the default ``www-dino``, you can freely choose any
  non-existing username. Just make sure to adapt the following steps and the
  systemd unit accordingly.

.. code-block:: console

  root@ubuntu-bionic:~# adduser --disabled-password --disabled-login \
    --system --home /var/dino www-dino

Dino
----

.. code-block:: console

  root@ubuntu-bionic:~# sudo -Hu www-dino pip3 install --user \
    https://github.com/Uberspace/dino/archive/master.zip#subdirectory=src

Basic Configuration
^^^^^^^^^^^^^^^^^^^

Create ``/etc/dino.cfg`` with the following content, adapt as needed.

.. code-block:: ini

  # a long (>64 chars) and random (alpha-numeric-ish) string of characters
  DINO_SECRET_KEY=
  # URL to your PowerDNS server API endpoint, e.g. https://yourpowerdns.com/api/v1
  DINO_PDNS_APIURL=
  # PowerDNS API key from /etc/pdns/pdns.conf
  DINO_PDNS_APIKEY=
  # comma-separated list of hostnames dino should be reachable under
  DINO_ALLOWED_HOSTS=
  # a place for dino to drop static files and other internal data; must be
  # writeable by dino and not publicly acccessible
  DINO_BASE_DIR=/var/dino

Service
^^^^^^^

To start dino automatically when your server boots up, create a new systemd
unit in ``/etc/systemd/system/dino.ini`` and add the following content.

.. warning::
  The path to uwsgi (``/usr/local/bin/uwsgi``) may vary on other distributions.
  To be on the safe side, use the command ``which uwsgi`` to get the path for
  your installation.

.. code-block:: ini

  [Unit]
  Description=uWSGI dino
  After=networking.target

  [Service]
  ExecStart=/usr/local/bin/uwsgi --http-socket :8080 --master --workers 8 --module dino.wsgi
  User=www-dino
  Restart=always
  KillSignal=SIGQUIT
  Type=notify
  StandardError=syslog
  NotifyAccess=all

  [Install]
  WantedBy=multi-user.target

Finally, load the newly create service:

.. code-block:: console

  root@ubuntu-bionic:~# systemctl daemon-reload

Finishing up
^^^^^^^^^^^^

Create a database
"""""""""""""""""

By default, a SQLite database is used.

.. code-block:: console

  root@ubuntu-bionic:~# sudo -Hu www-dino python3 -m dino migrate

Create an admin user
""""""""""""""""""""

The very first user has to be created using an interactive command. Additional
users can be created in the web interface, once we're up and running.

.. code-block:: console

  root@ubuntu-bionic:~# sudo -Hu www-dino python3 -m dino createsuperuser

Start dino
""""""""""

.. code-block:: console

  root@ubuntu-bionic:~# systemctl enable dino --now

Congratulations, is now running! You can verify this by querying the port directly:

.. code-block:: console

  root@ubuntu-bionic:~# curl 127.0.0.1:8080
  <h1>Bad Request (400)</h1>

Reverse Proxy
-------------

Even though dino is running, it's currently not possible to reach it from the
outside world (e.g. your browser). For that to happen we need a reverse proxy.
In our example nginx will be used, but you can use any other software like
Apache, Lighttpd or Traefik.

Installation
^^^^^^^^^^^^

.. code-block:: console

  root@ubuntu-bionic:~# apt install -y nginx

.. warning::

  Some distributions do not allow nginx to make network connections. This can
  be changed by enabling the appropriate SELinux boolean, like so:

  .. code-block:: console

    root@ubuntu-bionic:~# apt install -y policycoreutils
    root@ubuntu-bionic:~# setsebool httpd_can_network_connect true -P

Configuration
^^^^^^^^^^^^^

    proxy_set_header Host $host;

First, remove the default site, if present:

.. code-block:: console

  root@ubuntu-bionic:~# rm -f /etc/nginx/sites-enabled/default


Then, create our new configuration in ``/etc/nginx/sites-enabled/dino``:

.. code-block:: nginx

  server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
      proxy_set_header Host $host;
      proxy_pass http://localhost:8080;
    }
  }

.. note::

  The above configuration only includes the bare minimum - no HTTPS, caching or
  anything else considered state-of-the-art. Expand it according to best
  practices as needed.

Finishing up
^^^^^^^^^^^^

You're done! Fire up your browser and open the URL configured in your webserver.
Then you can log in using the account created earlier.