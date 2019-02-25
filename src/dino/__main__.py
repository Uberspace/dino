import os
import sys

# stolen from pretix (Apache 2.0), thanks!
# https://github.com/pretix/pretix/blob/master/src/pretix/__main__.py

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dino.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
