import contextlib
import distutils.util
import os


class Config():
    def __init__(self, prefix, env_files=None):
        self._prefix = prefix
        self._errors = []

        self._config_file = {}
        if env_files:
            self._load_env_files(env_files)

    def _load_env_files(self, env_files):
        """ load given .env files, latter ones overriding options in former ones. """
        with contextlib.ExitStack() as stack:
            env_files = [
                stack.enter_context(open(f, 'r'))
                for f in env_files
                if os.path.isfile(f)
            ]

            for f in env_files:
                # read all lines, skipping #comments and lines w/o key=value
                for l in f.readlines():
                    if l.lstrip()[0] == '#':
                        continue

                    k, sep, v = l.partition('=')

                    if sep != '=':
                        continue

                    self._config_file[k.strip()] = v.strip()

    def _env_key(self, key):
        return f'{self._prefix.upper()}_{key.upper()}'

    def add_error(self, msg):
        self._errors.append(msg)

    def _cast(self, value, cast):
        if cast == str:
            return value
        elif cast == list:
            return value.split(',')
        elif cast == bool:
            return distutils.util.strtobool(value)
        else:
            raise Exception(f'Invalid cast {cast}.')

    def get(self, key, default=None, cast=str):
        value = default
        env_key = self._env_key(key)

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
                '\n'.join(f'  {e}' for e in self._errors)
            )
            return False
