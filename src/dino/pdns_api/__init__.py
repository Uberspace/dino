import idna
import powerdns
from django.conf import settings
from powerdns.exceptions import PDNSError  # noqa


class PDNSNotFoundException(LookupError):
    pass


# allow underscores in zone and record names
# see https://github.com/kjd/idna/issues/50
idna.idnadata.codepoint_classes['PVALID'] = tuple(
    sorted(list(idna.idnadata.codepoint_classes['PVALID']) + [0x5f0000005f])
)


class pdns():
    def __init__(self):
        api_client = powerdns.PDNSApiClient(
            api_endpoint=settings.PDNS_APIURL,
            api_key=settings.PDNS_APIKEY
        )
        self.api = powerdns.PDNSEndpoint(api_client)

    @classmethod
    def _encode_name(cls, name):
        """ convert a record to punnycode format """
        assert isinstance(name, str)

        if name.startswith('*.'):
            return '*.' + idna.encode(name[2:]).decode('ascii')
        else:
            return idna.encode(name).decode('ascii')

    @classmethod
    def _decode_name(cls, name):
        """ convert a record from punnycode format """
        assert isinstance(name, str)

        if name.startswith('*.'):
            return '*.' + idna.decode(name[2:])
        else:
            return idna.decode(name)

    @property
    def _server(self):
        return self.api.servers[0]

    def get_zones(self):
        return [
            self._decode_name(z.name)
            for z in self._server.zones
        ]

    def create_zone(self, name, kind, nameservers, masters):
        if kind not in ('Native', 'Master', 'Slave'):
            raise Exception(f'kind must be Native, Master or Slave; not {kind}.')

        name = self._encode_name(name)
        self._server.create_zone(name, kind, nameservers, masters)

    def delete_zone(self, name):
        name = self._encode_name(name)
        self._server.delete_zone(name)

    def _encode_content(self, rtype, content):
        """ convert a record to PowerDNS format """
        if rtype == 'TXT':
            content = content.replace("\\", "\\\\")  # \ => \\
            content = content.replace('"', '\\"')     # " => \"
            content = f'"{content}"'

        return content

    def _decode_content(self, rtype, content):
        """ convert a record from PowerDNS format """
        if rtype == 'TXT':
            content = content.replace('\\"', '"')    # \" => "
            content = content.replace("\\\\", "\\")  # \\ => \
            if content.endswith('"'):
                content = content[:-1]
            if content.startswith('"'):
                content = content[1:]

        return content

    def get_all_records(self, zone):
        zone = self._encode_name(zone)
        zone = self._server.get_zone(zone)
        if zone is None:
            raise PDNSNotFoundException()
        axfr = zone._get(zone.url + '/export')['zone'].strip()
        lines = [r.split('\t') for r in axfr.split('\n')]
        if lines and len(lines[0]) == 5:
            # https://github.com/Uberspace/dino/issues/83
            return (
                {
                    'zone': self._decode_name(zone.name),
                    'name': self._decode_name(r[0]),
                    'ttl': int(r[1]),
                    'type': r[2],  # IN
                    'rtype': r[3],  # A, AAAA, SOA, ...
                    'content': self._decode_content(r[3], r[4]),
                }
                for r in lines
            )
        else:
            return (
                {
                    'zone': self._decode_name(zone.name),
                    'name': self._decode_name(r[0]),
                    'ttl': int(r[1]),
                    'rtype': r[2],
                    'content': self._decode_content(r[2], r[3]),
                }
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
        zone = self._encode_name(zone)
        name = self._encode_name(name)
        contents = [self._encode_content(rtype, c) for c in contents]
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
        if not any(r['content'] == content for r in old_records):
            raise PDNSNotFoundException()  # record is already gone

        ttl = old_records[0]['ttl']
        contents = [r['content'] for r in old_records if r['content'] != content]
        self._update_records(zone, name, rtype, ttl, contents)

    def update_record(self, zone, name, rtype, old_content, new_ttl, new_content):
        old_records = list(self.get_records(zone, name, rtype))

        if not old_records:
            raise PDNSNotFoundException()  # record is already gone
        if not any(r['content'] == old_content for r in old_records):
            raise PDNSNotFoundException()  # record is already gone

        contents = [r['content'] for r in old_records if r['content'] != old_content]
        contents.append(new_content)

        self._update_records(zone, name, rtype, new_ttl, contents)


__all__ = [
    'pdns',
]
