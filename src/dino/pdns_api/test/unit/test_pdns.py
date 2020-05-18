import powerdns
import pytest

from ... import PDNSNotFoundException


@pytest.fixture
def pdns():
    from ... import pdns
    return pdns()


@pytest.fixture
def client(mocker):
    client = powerdns.PDNSApiClient('', '')
    server = powerdns.interface.PDNSServer(client, {
        "type": "Server",
        "id": "localhost",
        "url": "/api/v1/servers/localhost",
        "daemon_type": "recursor",
        "version": "VERSION",
        "config_url": "/api/v1/servers/localhost/config{/config_setting}",
        "zones_url": "/api/v1/servers/localhost/zones{/zone}",
    })
    mocker.patch('powerdns.interface.PDNSEndpoint.servers', new_callable=mocker.PropertyMock, return_value=[server])
    return client, server


# putting the mocks directly into the test functions doesn't mock them
@pytest.fixture
def mock_lib_pdns_create_zone(mocker, client):
    return mocker.patch('powerdns.interface.PDNSServer.create_zone')


@pytest.mark.parametrize('kind', ['Native', 'Master', 'Slave'])
def test_pdns_create_zone(pdns, kind, mock_lib_pdns_create_zone):
    pdns.create_zone('example.com.', 'Native', [], ['ns1'])
    mock_lib_pdns_create_zone.assert_called_once_with('example.com.', 'Native', [], ['ns1'])


def test_pdns_create_zone_punycode(pdns, mock_lib_pdns_create_zone):
    pdns.create_zone('sömething.com.', 'Native', [], ['ns1'])
    mock_lib_pdns_create_zone.assert_called_once_with('xn--smething-n4a.com.', 'Native', [], ['ns1'])


def test_pdns_create_zone_kind(pdns):
    with pytest.raises(Exception) as excinfo:
        pdns.create_zone('example.com.', 'Blargh', [], [])
    assert 'Native' in str(excinfo)


@pytest.fixture
def mock_lib_pdns_delete_zone(mocker, client):
    return mocker.patch('powerdns.interface.PDNSServer.delete_zone')


def test_pdns_delete_zone(pdns, mock_lib_pdns_delete_zone):
    pdns.delete_zone('example.com.')
    mock_lib_pdns_delete_zone.assert_called_once_with('example.com.')


def test_pdns_delete_zone_punycode(pdns, mock_lib_pdns_delete_zone):
    pdns.delete_zone('sömething.com')
    mock_lib_pdns_delete_zone.assert_called_once_with('xn--smething-n4a.com')


@pytest.fixture
def mock_lib_pdns_get_zone(mocker, client):
    def f(zone):
        return powerdns.interface.PDNSZone(client[0], client[1], {
            'name': zone,
            'url': '',
        })

    return mocker.patch('powerdns.interface.PDNSServer.get_zone', side_effect=f)


@pytest.fixture
def mock_lib_pdns_axfr(mocker):
    def f(path, method):
        if path == '/servers/localhost/zones/example.com./export':
            return {
                'zone': '''
www.example.com.\t300\tAAAA\t1.2.3.4
www.example.com.\t300\tAAAA\t4.3.2.1
mail.example.com.\t600\tA\t4.3.2.1
foo.example.com.\t600\tTXT\t"\\\\\\"\\""
'''
            }
        elif path == '/servers/localhost/zones/xn--smething-n4a.com./export':
            return {
                'zone': '''
xn--smething-n4a.com.\t300\tA\t1.2.3.4
xn--wht-rla.xn--smething-n4a.com.\t300\tA\t4.3.2.1
'''
            }
        else:
            raise Exception('unknown domain, fix the test or extend this mock.')

    return mocker.patch('powerdns.client.PDNSApiClient.request', side_effect=f)


def test_pdns_get_all_records(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_all_records('example.com.')
    r = list(r)
    assert r == [
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '4.3.2.1'},
        {'zone': 'example.com.', 'name': 'mail.example.com.', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
        {'zone': 'example.com.', 'name': 'foo.example.com.', 'ttl': 600, 'rtype': 'TXT', 'content': '\\""'},
    ]


def test_pdns_get_all_records_punycode(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_all_records('sömething.com.')
    r = list(r)
    assert r == [
        {'zone': 'sömething.com.', 'name': 'sömething.com.', 'ttl': 300, 'rtype': 'A', 'content': '1.2.3.4'},
        {'zone': 'sömething.com.', 'name': 'whät.sömething.com.', 'ttl': 300, 'rtype': 'A', 'content': '4.3.2.1'},
    ]


def test_pdns_get_records(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com.')
    r = list(r)
    assert r == [
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '4.3.2.1'},
        {'zone': 'example.com.', 'name': 'mail.example.com.', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
        {'zone': 'example.com.', 'name': 'foo.example.com.', 'ttl': 600, 'rtype': 'TXT', 'content': '\\""'},
    ]


def test_pdns_get_records_name(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com.', name='www.example.com.')
    r = list(r)
    assert r == [
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
        {'zone': 'example.com.', 'name': 'www.example.com.', 'ttl': 300, 'rtype': 'AAAA', 'content': '4.3.2.1'},
    ]


def test_pdns_get_records_rtype(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com.', rtype='A')
    r = list(r)
    assert r == [
        {'zone': 'example.com.', 'name': 'mail.example.com.', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
    ]


@pytest.fixture
def mock_create_records(mocker):
    return mocker.patch('powerdns.interface.PDNSZone.create_records')


def test_pdns_create_record(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.create_record('example.com.', 'www.example.com.', 'AAAA', 400, '0 example.org.')
    mock_create_records.assert_called_once()
    rrsets = mock_create_records.call_args[0]
    assert len(rrsets) == 1
    assert rrsets[0][0]['name'] == 'www.example.com.'
    assert rrsets[0][0]['type'] == 'AAAA'
    assert rrsets[0][0]['ttl'] == 400
    assert rrsets[0][0]['records'] == [
        {'content': '1.2.3.4', 'disabled': False},
        {'content': '4.3.2.1', 'disabled': False},
        {'content': '0 example.org.', 'disabled': False},
    ]


def test_pdns_create_record_quotes(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.create_record('example.com.', 'www.example.com.', 'TXT', 400, '"\\')
    mock_create_records.assert_called_once()
    rrsets = mock_create_records.call_args[0]
    assert rrsets[0][0]['records'] == [
        {'content': r'"\"\\"', 'disabled': False}
    ]


def test_pdns_create_record_punycode(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.create_record('sömething.com.', 'mail.sömething.com.', 'MX', 400, '0 example.org')
    mock_create_records.assert_called_once()
    mock_lib_pdns_get_zone.assert_called_with('xn--smething-n4a.com.')
    rrsets = mock_create_records.call_args[0]
    assert rrsets[0][0]['name'] == 'mail.xn--smething-n4a.com.'
    assert rrsets[0][0]['type'] == 'MX'
    assert rrsets[0][0]['ttl'] == 400
    assert rrsets[0][0]['records'] == [
        {'content': '0 example.org', 'disabled': False}
    ]


def test_pdns_delete_record(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.delete_record('example.com.', 'www.example.com.', 'AAAA', '1.2.3.4')
    mock_create_records.assert_called_once()
    rrsets = mock_create_records.call_args[0]
    assert len(rrsets) == 1
    assert rrsets[0][0]['name'] == 'www.example.com.'
    assert rrsets[0][0]['type'] == 'AAAA'
    assert rrsets[0][0]['ttl'] == 300
    assert rrsets[0][0]['records'] == [
        {'content': '4.3.2.1', 'disabled': False},
    ]


@pytest.mark.parametrize('args', [
    ['example.com.', 'www.example.com.', 'AAAA', '5.5.5.5'],
    ['example.com.', 'www.example.com.', 'A', '1.2.3.4'],
])
def test_pdns_delete_record_gone(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records, args):
    with pytest.raises(PDNSNotFoundException):
        pdns.delete_record(*args)
    mock_create_records.assert_not_called()


def test_pdns_update_record(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.update_record(
        'example.com.',
        'www.example.com.',
        'AAAA',
        '1.2.3.4',
        '400',
        '1.2.3.5'
    )
    mock_create_records.assert_called_once()
    rrsets = mock_create_records.call_args[0]
    assert len(rrsets) == 1
    assert rrsets[0][0]['name'] == 'www.example.com.'
    assert rrsets[0][0]['type'] == 'AAAA'
    assert rrsets[0][0]['ttl'] == '400'
    assert rrsets[0][0]['records'] == [
        {'content': '4.3.2.1', 'disabled': False},
        {'content': '1.2.3.5', 'disabled': False},
    ]


punyzones = [
    ['example.com', 'example.com'],
    ['*.example.com', '*.example.com'],
    ['exämple.com', 'xn--exmple-cua.com'],
    ['*.exämple.com', '*.xn--exmple-cua.com'],
    ['asd.cöm', 'asd.xn--cm-fka'],
    ['exa_mple.com.', 'exa_mple.com.'],
]


@pytest.mark.parametrize('name,punycode', punyzones)
def test_encode_name(pdns, name, punycode):
    assert pdns._encode_name(name) == punycode


@pytest.mark.parametrize('punycode,name', punyzones)
def test_decode_name(pdns, punycode, name):
    assert pdns._decode_name(name) == punycode
