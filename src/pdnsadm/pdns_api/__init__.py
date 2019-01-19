import powerdns
from django.conf import settings


class pdns():
    def __init__(self):
        api_client = powerdns.PDNSApiClient(
            api_endpoint=settings.PDNS_APIURL,
            api_key=settings.PDNS_APIKEY
        )
        self.api = powerdns.PDNSEndpoint(api_client)

    @property
    def _server(self):
        return self.api.servers[0]

    def get_zones(self):
        return self._server.zones

    def get_records(self, zone):
        zone = self._server.get_zone(zone)
        axfr = zone._get(zone.url + '/export')['zone'].strip()
        lines = (r.split('\t') for r in axfr.split('\n'))
        return [
            {'name': r[0], 'ttl': r[1], 'type': r[2], 'content': r[3]}
            for r in lines
        ]


__all__ = [
    'pdns',
]
