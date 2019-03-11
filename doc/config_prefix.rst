Configuration
=============

Dino provides a variety of configuration options. Have a quick list through the
list to see which ones are relevant to you!

Location
--------

There are multiple ways to set configuration options:

1. File ``/etc/dino.cfg``, global config
2. File ``~/.dino.cfg``, user config
3. File ``./dini.cfg``, local config
4. Process Environment (e.g. ``$DINO_BASE_DIR``)

They are loaded in the order above; later files overwrite earlier ones.

File Format
-----------

Configuration is stored in a simple, non-nested ``key=value`` format. Comments
can be added using ``#`` on dedicated lines. Lines without ``=`` are ignored.

.. code-block:: ini

  # this is a comment
  DINO_BASE_DIR=/opt/dino
  DINO_SECRET_KEY = verysecret

Options
-------
