from io import StringIO

import pytest

from ...config import Config, Setting


@pytest.fixture
def mock_config_open(mocker):
    def mock_open(path, *args, **kwargs):
        if path.startswith('/etc'):
            return StringIO("""
DINO_BLA=etc
DINO_FOO=etc
            """.strip())
        elif path.startswith('/home'):
            return StringIO("""
DINO_FOO=home
            """.strip())
        elif path.startswith('/comments'):
            return StringIO("""
# this is a comment
DINO_FOO=home
someinvalidline
#DINO_FOO=ignorethis
            """.strip())
        else:
            raise FileNotFoundError()

    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', mock_open)


def test_config_default():
    c = Config('DINO')
    c.get('BLA', 'somedefault')
    assert c.check_errors()


def test_config_env(monkeypatch):
    c = Config('DINO')
    monkeypatch.setenv('DINO_BLA', 'env')
    assert c.get('BLA') == 'env'
    assert c.check_errors()


def test_config_env_list(monkeypatch):
    c = Config('DINO')
    monkeypatch.setenv('DINO_BLA', 'a,b,c2')
    assert c.get('BLA', cast=list) == ['a', 'b', 'c2']
    assert c.check_errors()


@pytest.mark.parametrize('value,out', [
    ('true', True),
    ('True', True),
    ('false', False),
    ('False', False),
])
def test_config_env_bool(monkeypatch, value, out):
    c = Config('DINO')
    monkeypatch.setenv('DINO_BLA', value)
    assert c.get('BLA', cast=bool) == out
    assert c.check_errors()


def test_config_env_bool_invalid(monkeypatch, capsys):
    c = Config('DINO')
    monkeypatch.setenv('DINO_BLA', 'foo')
    assert c.get('BLA', cast=bool) is None
    assert not c.check_errors()
    captured = capsys.readouterr()
    assert '$DINO_BLA' in captured.err


def test_config_invalid_cast():
    c = Config('DINO')
    with pytest.raises(Exception) as excinfo:
        c.get('BLA', cast=tuple)
    assert 'Invalid cast' in str(excinfo)


def test_config_missing_value(capsys):
    c = Config('DINO')
    assert c.get('BLA') is None
    assert not c.check_errors()
    captured = capsys.readouterr()
    assert '$DINO_BLA' in captured.err


def test_config_files(mock_config_open):
    c = Config('DINO',
        [
            '/etc/dino.cfg',
            '/home/bla/.dino.cfg',
        ]
    )
    assert c.get('BLA') == 'etc'
    assert c.get('FOO') == 'home'
    c.check_errors()


def test_config_missing_file():
    c = Config('DINO', ['/does/not/exist.cfg'])
    assert c.get('BLA', 'somedefault') == 'somedefault'
    assert c.check_errors()


def test_config_file_format(mock_config_open):
    c = Config('DINO', ['/comments/something.cfg'])
    assert c.get('FOO') == 'home'
    assert c.check_errors()


def test_config_full(mock_config_open, monkeypatch):
    c = Config('DINO',
        [
            '/etc/dino.cfg',
            '/home/bla/.dino.cfg',
        ]
    )
    monkeypatch.setenv('DINO_BLA', 'env')
    assert c.get('BLA') == 'env'
    assert c.get('FOO') == 'home'
    assert c.check_errors()


@pytest.mark.parametrize('cast,cast_str', [
    ((str, 'string')),
    ((list, 'list')),
    ((bool, 'boolean')),
    ((set, "<class 'set'>")),
])
def test_config_setting(cast, cast_str):
    s = Setting('BASE_DIR', 'DINO_BASE_DIR', None, cast, False, '', '')
    assert s.cast_str == cast_str


def test_config_settings_human():
    c = Config('DINO')
    c.get('BASE_DIR', cast=str, django=False, example='example', doc='doc')
    c.get('SECRET_KEY', default='default', cast=str, django=True, example='example', doc='doc')
    r = list(c._settings_human())
    assert len(r) == 2
    assert r[0][0] == 'BASE_DIR'
    assert r[0][1] == 'DINO_BASE_DIR'
    assert r[0][2] == {
        'type': 'string',
        'description': 'doc',
        'required': 'yes',
        'default': None,
        'example': 'example',
    }
    assert r[1][0] == 'SECRET_KEY'
    assert r[1][1] == 'DINO_SECRET_KEY'
    assert r[1][2] == {
        'type': 'string',
        'description': 'doc',
        'required': 'no',
        'default': 'default',
        'example': 'example',
        'django docs': 'https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY',
    }


def test_config_settings_rst():
    c = Config('DINO')
    c.get('BASE_DIR', cast=str, django=False, example='example', doc='doc')
    c.get('SECRET_KEY', default='default', cast=str, django=True, example='exampleee', doc='DOCuMENTATION')
    r = c.settings_rst()
    assert 'DINO_BASE_DIR' in r
    assert 'SECRET_KEY' in r
    assert 'djangoproject.com' in r
    assert 'exampleee' in r
    assert 'DOCuMENTATION' in r


def test_config_settings_plaintext():
    c = Config('DINO')
    c.get('BASE_DIR', cast=str, django=False, example='example', doc='doc')
    c.get('SECRET_KEY', default='default', cast=str, django=True, example='exampleee', doc='DOCuMENTATION')
    r = c.settings_plaintext()
    assert 'DINO_BASE_DIR' in r
    assert 'SECRET_KEY' in r
    assert 'djangoproject.com' in r
    assert 'exampleee' in r
    assert 'DOCuMENTATION' in r


def test_config_settings_human_empty():
    c = Config('DINO')
    r = list(c._settings_human())
    assert len(r) == 0
