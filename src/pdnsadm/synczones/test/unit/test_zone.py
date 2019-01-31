import pytest

from ...models import Zone


def test_zone_str():
    assert 'example.com.' in str(Zone(name='example.com.'))


@pytest.mark.django_db()
def test_zone_import_from_powerdns(MockPDNSZone):
    Zone().import_from_powerdns((
        MockPDNSZone('example.com.'),
        MockPDNSZone('example.org.'),
        MockPDNSZone('example.co.uk.'),
    ))

    assert Zone.objects.all().count() == 3
    assert {
        'example.com.',
        'example.org.',
        'example.co.uk.',
    } == set(Zone.objects.all().values_list('name', flat=True))
