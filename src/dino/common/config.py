import contextlib
from collections import OrderedDict
import distutils.util
import os
import sys


class Setting():
    def __init__(self, key, env_key, default, cast, django, example, doc):
        self.key = key
        self.env_key = env_key
        self.default = default
        self.cast = cast
        self.django = django
        self.example = example
        self.doc = doc

    @property
    def cast_str(self):
        if self.cast == str:
            return 'string'
        elif self.cast == list:
            return 'list'
        elif self.cast == bool:
            return 'boolean'
        else:
            return str(self.cast)


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
        self.settings = []

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

    def get(self, key, default=None, cast=str, django=False, example=None, doc=None):
        value = default
        env_key = self._env_key(key)

        self.settings.append(Setting(key, env_key, default, cast, django, example, doc))

        if cast not in self.CAST_NAMES:
            raise Exception(f'Invalid cast {cast}.')

        try:
            with contextlib.suppress(KeyError):
                value = self._cast(self._config_file[env_key], cast)
            with contextlib.suppress(KeyError):
                value = self._cast(os.environ[env_key], cast)
        except ValueError as exc:
            self.add_error(f'Configuration value {key}/${env_key} was invalid: {exc}.')
            return None

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

    def _settings_human(self):
        for setting in self.settings:
            fields = []

            fields.append(('type', setting.cast_str))
            fields.append(('description', setting.doc))
            fields.append(('required', 'yes' if setting.default is None else 'no'))
            fields.append(('default', setting.default))
            fields.append(('example', setting.example))

            if setting.django:
                fields.append(('django docs', 'https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-{setting.key}'))

            yield (setting.env_key, OrderedDict(fields))

    def settings_rst(self):
        result = ""

        for env_key, fields in self._settings_human():
            result += f'{env_key}\n'
            result += '^' * len(env_key) + '\n\n'
            result += (fields.pop('description') or '') + '\n\n'
            result += '\n'.join(f'* **{k}**: ``{v}``' for k, v in fields.items()) + '\n\n'

        return result

    def settings_plaintext(self):
        result = ""

        for env_key, fields in self._settings_human():
            result += env_key + '\n'
            result += '\n'.join(f'  {k:11}: {v}' for k, v in fields.items()) + '\n'

        return result
