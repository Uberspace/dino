import powerdns
from django.conf import settings


def records_axfr(self):
    """Get zone's records as AXFR"""
    lines = (r.split('\t') for r in self._get(self.url + '/export')['zone'].strip().split('\n'))
    return [
        {'name': r[0], 'ttl': r[1], 'type': r[2], 'content': r[3]}
        for r in lines
    ]

powerdns.interface.PDNSZone.records_axfr = records_axfr

class pdns():
    def __init__(self):
        api_client = powerdns.PDNSApiClient(
            api_endpoint=settings.PDNS_APIURL,
            api_key=settings.PDNS_APIKEY
        )
        self.api = powerdns.PDNSEndpoint(api_client)

    @property
    def server(self):
        return self.api.servers[0]

__all__ = [
    'pdns',
]
