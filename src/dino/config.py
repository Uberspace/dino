import distutils.util
import os


class Config():
    def __init__(self, prefix):
        self._prefix = prefix
        self._errors = []

    def _env_key(self, key):
        return f'{self._prefix.upper()}_{key.upper()}'

    def add_error(self, msg):
        self._errors.append(msg)

    def get(self, key, default=None, cast=str):
        env_key = self._env_key(key)

        try:
            value = os.environ[env_key]
        except LookupError:
            if default is None:
                self.add_error(f'Environment variable ${env_key} is not set.')
                return None
            else:
                return default

        if cast == str:
            return value
        elif cast == list:
            return value.split(',')
        elif cast == bool:
            return distutils.util.strtobool(value)
        else:
            raise Exception(f'Invalid cast {cast} for setting {key}.')

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
