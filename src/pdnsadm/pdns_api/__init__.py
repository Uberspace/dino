import powerdns
from django.conf import settings
from powerdns.exceptions import *


class PDNSNotFoundException(LookupError):
    pass


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

    def create_zone(self, name, kind, nameservers):
        if kind not in ('Native', 'Master', 'Slave'):
            raise Exception(f'kind must be Native, Master or Slave; not {kind}.')

        self._server.create_zone(name, kind, nameservers)

    def delete_zone(self, name):
        self._server.delete_zone(name)

    def get_all_records(self, zone):
        zone = self._server.get_zone(zone)
        if zone is None:
            raise PDNSNotFoundException()
        axfr = zone._get(zone.url + '/export')['zone'].strip()
        lines = (r.split('\t') for r in axfr.split('\n'))
        return (
            {'name': r[0], 'ttl': int(r[1]), 'rtype': r[2], 'content': r[3]}
            for r in lines
        )

    def get_records(self, zone, name=None, rtype=None):
        """ get all records within zone whose name and rtype match (if given). """
        if name is None and rtype is None:
            return list(self.get_all_records(zone))
        else:
            return [
                r for r in self.get_all_records(zone)
                if
                    (r['name'] == name or name is None) and
                    (r['rtype'] == rtype or rtype is None)
            ]

    def _update_records(self, zone, name, rtype, ttl, contents):
        assert isinstance(contents, list)
        rrset = powerdns.RRSet(name, rtype, contents, ttl)
        zone = self._server.get_zone(zone)
        zone.create_records([rrset])

    def create_record(self, zone, name, rtype, ttl, content):
        contents = [r['content'] for r in self.get_records(zone, name, rtype)]
        contents.append(content)
        self._update_records(zone, name, rtype, ttl, contents)

    def delete_record(self, zone, name, rtype, content):
        old_records = list(self.get_records(zone, name, rtype))

        if not old_records:
            raise PDNSNotFoundException()  # record is already gone

        ttl = old_records[0]['ttl']
        contents = [r['content'] for r in old_records if r['content'] != content]
        self._update_records(zone, name, rtype, ttl, contents)


__all__ = [
    'pdns',
]
