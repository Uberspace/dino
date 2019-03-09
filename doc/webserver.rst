Webserver
=========

Even though dino is running, it's currently not possible to reach it from the
outside world (e.g. your browser). For that to happen we need a reverse proxy.
In our example nginx will be used, but you can use any other software like
Apache, Lighttpd or Traefik.

.. note::

  Just like the pip setup guide, this guide assumes a fresh ubuntu 18.04 bionic
  box. Most of the steps are the same or easily adapted for other distributions.

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

.. note::

  The above configuration only includes the bare minimum - no HTTPS, caching or
  anything else considered state-of-the-art. Expand it according to best
  practices as needed.

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
