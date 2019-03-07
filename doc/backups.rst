Backups
=======

Dino does currently not store any data outside the database. Should there be a
need to store data outside the database in future releases, it will be saved
inside the ``$DINO_BASE_DIR`` directory (e.g. ``/opt/dino``). If you want your
setup to be futureproof, make backups of it.

For now, all you have to do is backup your database. Below are a couple of
common options. 

SQLite
------

By default dino uses a SQLite database, which is just a file on your disk. To
back it up copy ``$DINO_BASE_DIR/db.sqlite3`` (e.g. ``/opt/dino/db.sqlite3``) to
somewhere safe outside the host.

PostgreSQL
----------

For most setups a simple ``pg_dump`` backup will suffice. For write-heavy
setups a more robust primary/secondary backup solution might be prefered.

.. code-block:: console

  postgres@host:~$ pg_dump --clean --create --file=dino_$(date -I).sql dino

Refer to `the PostgreSQL manual`_ for further instructions.

.. _`the PostgreSQL manual`: https://www.postgresql.org/docs/current/backup-dump.html

MySQL / MariaDB
---------------

For most setups a simple ``mysqldump`` backup will suffice. For write-heavy
setups a more robust primary/secondary backup solution might be prefered.

.. code-block:: console

  root@host:~# mysqldump --single-transaction --add-drop-database --databases dino > dino_$(date -I).sql

Refer to `the MySQL manual`_ for further instructions.

.. _`the MySQL manual`: https://dev.mysql.com/doc/refman/8.0/en/backup-methods.html
