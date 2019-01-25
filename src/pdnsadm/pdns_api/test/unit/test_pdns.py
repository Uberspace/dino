import pytest
import powerdns

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
    pdns.create_zone('example.com.', 'Native', [])
    mock_lib_pdns_create_zone.assert_called_once_with('example.com.', 'Native', [])

def test_pdns_create_zone_kind(pdns):
    with pytest.raises(Exception) as excinfo:
        pdns.create_zone('example.com.', 'Blargh', [])
    assert 'Native' in str(excinfo)

@pytest.fixture
def mock_lib_pdns_delete_zone(mocker, client):
    return mocker.patch('powerdns.interface.PDNSServer.delete_zone')

def test_pdns_delete_zone(pdns, mock_lib_pdns_delete_zone):
    pdns.delete_zone('example.com.')
    mock_lib_pdns_delete_zone.assert_called_once_with('example.com.')

@pytest.fixture
def mock_lib_pdns_get_zone(mocker, client):
    return mocker.patch('powerdns.interface.PDNSServer.get_zone',
        return_value=powerdns.interface.PDNSZone(client[0], client[1], {
            'name': 'example.com.',
            'url': '',
        })
    )

@pytest.fixture
def mock_lib_pdns_axfr(mocker):
    return mocker.patch('powerdns.client.PDNSApiClient.request',
        return_value={
            'zone': '''
www.example.com\t300\tAAAA\t1.2.3.4
www.example.org\t600\tA\t4.3.2.1
'''
        }
    )

def test_pdns_get_all_records(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_all_records('example.com')
    r = list(r)
    assert r == [
        {'name': 'www.example.com', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
        {'name': 'www.example.org', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
    ]

def test_pdns_get_records(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com')
    r = list(r)
    assert r == [
        {'name': 'www.example.com', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
        {'name': 'www.example.org', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
    ]

def test_pdns_get_records_name(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com', name='www.example.com')
    r = list(r)
    assert r == [
        {'name': 'www.example.com', 'ttl': 300, 'rtype': 'AAAA', 'content': '1.2.3.4'},
    ]

def test_pdns_get_records_rtype(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone):
    r = pdns.get_records('example.com', rtype='A')
    r = list(r)
    assert r == [
        {'name': 'www.example.org', 'ttl': 600, 'rtype': 'A', 'content': '4.3.2.1'},
    ]

@pytest.fixture
def mock_create_records(mocker):
    return mocker.patch('powerdns.interface.PDNSZone.create_records')

def test_pdns_create_record(pdns, mock_lib_pdns_axfr, mock_lib_pdns_get_zone, mock_create_records):
    pdns.create_record('example.org', 'www.example.org', 'A', 300, '0 example.org')
    mock_create_records.assert_called_once()
    rrsets = mock_create_records.call_args[0]
    assert len(rrsets) == 1
    assert rrsets[0][0]['name'] == 'www.example.org'
    assert rrsets[0][0]['type'] == 'A'
    assert rrsets[0][0]['ttl'] == 300
    assert rrsets[0][0]['records'] == [
        {'content': '4.3.2.1', 'disabled': False},
        {'content': '0 example.org', 'disabled': False},
    ]
