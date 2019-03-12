Database
========

Before we can start installing dino the database needs to be prepared. There
are no special requrements so any database `supported by django`_ may be used.
Official support is given for SQLite, PostgreSQL and MySQL/MariaDB.

With the exception of SQLite these instructions assume that your database system
was installed, intialized, correctly configured and started and only deals with
aspects relevant to our setup.

.. _`supported by django`: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DATABASE-ENGINE

SQLite
------

By default dino uses a SQLite database, which is just a file on your disk. In
this case, no configuration is necessary. Please keep in mind that, while being
a capable database, SQLite does not scale well and has weaker guarantees than
server-based database solutions like PostgreSQL.

PostgreSQL
----------

`The Wikipedia <https://en.wikipedia.org/wiki/PostgreSQL>`_ describes PostgreSQL as:

  (...) an open source object-relational database management system with an
  emphasis on extensibility and standards compliance.

Create a new user and database for dino:

.. code-block:: console

  postgres@host:~$ createuser dino -P
  Enter password for new role: ******
  Enter it again: ******
  postgres@host:~$ createdb dino --owner=dino

.. note::
  If you are installing dino using ``pip``, the setup can be password-less using
  a UNIX socket connection and `Peer Authentication`_.

Install the python PostgreSQL client library:

.. code-block:: console

  root@host:~# pip install psycopg2
  Collecting psycopg2
    Cache entry deserialization failed, entry ignored
    Downloading https://files.pythonhosted.org/packages/...
  (...)
  Successfully installed psycopg2-2.7.7

.. _`Peer Authentication`: https://www.postgresql.org/docs/current/auth-peer.html

MySQL / MariaDB
---------------

`MariaDB <https://mariadb.org/about/>`_ describes itself as:

  (...) one of the most popular database servers in the world. It’s made by the
  original developers of MySQL and guaranteed to stay open source. Notable users
  include Wikipedia, WordPress.com and Google.

Create a new user and database for dino:

.. code-block:: console

  root@host:~# mysql
  mysql> CREATE DATABASE dino DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
  mysql> GRANT ALL PRIVILEGES ON dino.* TO dino@'localhost' IDENTIFIED BY '*********';
  mysql> FLUSH PRIVILEGES;

Install the python MySQL client library:

.. code-block:: console

  root@host:~# pip install mysqlclient
  Collecting mysqlclient
  Cache entry deserialization failed, entry ignored
  Downloading https://files.pythonhosted.org/packages/...
  (...)
  Successfully installed mysqlclient-1.4.2.post1
