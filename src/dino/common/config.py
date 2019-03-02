import contextlib
import distutils.util
import os
import sys


class Config():
    CASTS = {
        str: lambda v: v,
        list: lambda v: v.split(','),
        bool: distutils.util.strtobool,
    }
    CAST_NAMES = CASTS.keys()

    def __init__(self, prefix, env_files=None):
        self._prefix = prefix
        self._errors = []

        if env_files:
            self._config_file = self._load_env_files(env_files)
        else:
            self._config_file = {}

    def _load_env_file(self, env_file):
        """
        read all lines in a key=value format, return kv-pairs
        skipping #comments and lines w/o key=value
        """
        with open(env_file) as f:
            for l in f.readlines():
                if l.lstrip()[0] == '#':
                    continue

                k, sep, v = l.partition('=')

                if sep != '=':
                    continue

                yield (k.strip(), v.strip())

    def _load_env_files(self, env_files):
        """ load given .env files, latter ones overriding options in former ones. """
        config = {}

        for env_file in env_files:
            if not os.path.isfile(env_file):
                continue

            config.update(dict(self._load_env_file(env_file)))

        return config

    def _env_key(self, key):
        return f'{self._prefix.upper()}_{key.upper()}'

    def add_error(self, msg):
        self._errors.append(msg)

    def _cast(self, value, cast):
        return self.CASTS[cast](value)

    def get(self, key, default=None, cast=str):
        value = default
        env_key = self._env_key(key)

        if cast not in self.CAST_NAMES:
            raise Exception(f'Invalid cast {cast}.')

        with contextlib.suppress(KeyError):
            value = self._cast(self._config_file[env_key], cast)
        with contextlib.suppress(KeyError):
            value = self._cast(os.environ[env_key], cast)

        if value is None:
            self.add_error(f'Configuration value {key}/${env_key} is required and not set.')
            return None

        return value

    def check_errors(self):
        if not self._errors:
            return True
        else:
            print(
                'Dino cannot be started because of missing configuration values.\n'
                'Please correct the errors below:\n' +
                '\n'.join(f'  {e}' for e in self._errors),
                file=sys.stderr,
            )
            return False
