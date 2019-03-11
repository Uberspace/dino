Webserver
=========

Even though dino is running, it's currently not possible to reach it from the
outside world (e.g. your browser). For that to happen we need a reverse proxy.
In our example nginx will be used, but you can use any other software like
Apache, Lighttpd or Traefik.

.. note::

  Just like the pip setup guide, this guide assumes a fresh ubuntu 18.04 bionic
  box. Most of the steps are the same or can be easily adapted for other
  distributions.

Installation
------------

.. code-block:: console

  root@ubuntu-bionic:~# apt install -y nginx

.. warning::

  Some distributions do not allow nginx to make network connections. This can
  be changed by enabling the appropriate SELinux boolean, like so:

  .. code-block:: console

    root@ubuntu-bionic:~# apt install -y policycoreutils
    root@ubuntu-bionic:~# setsebool httpd_can_network_connect true -P

Configuration
-------------

First, remove the default site, if present:

.. code-block:: console

  root@ubuntu-bionic:~# rm -f /etc/nginx/sites-enabled/default


Then, create our new configuration in ``/etc/nginx/sites-enabled/dino``:

.. code-block:: nginx

  server {
    # this configuration does not include any HTTP, which is a bad idea.
    # use the generator below or any other resource to add transport encryption
    # to your requests.
    # https://mozilla.github.io/server-side-tls/ssl-config-generator/
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-Port $server_port;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_pass http://localhost:8080;
    }
  }

Static Files
------------

Dino is able to serve all requests itself - this includes static files like
CSS or JavaScript. For small setups, pinging python and django for each and
every static file is quite fast enough; refer to the `whitenoise documentation`_
details. Bigger setups with a high volume of requests might benefit from caching
those requests.

You can cache everything that is requested from the ``/static/`` directory. URLs
look like ``/static/style/zoneeditor.d7de63624ec9.css``, contain a hash, which
changes when the content changes. This means that you can cache them without any
kind of timeout or cache invalidation.

.. _`whitenoise documentation`: http://whitenoise.evans.io/en/stable/index.html#isn-t-serving-static-files-from-python-horribly-inefficient

Start nginx
-----------

.. code-block:: console

  root@ubuntu-bionic:~# systemctl enable nginx
  root@ubuntu-bionic:~# systemctl restart nginx

Finishing up
------------

You're done! Fire up your browser and open the URL configured in your webserver.
Then you can log in using the account created using the ``createsuperuser``
command.
