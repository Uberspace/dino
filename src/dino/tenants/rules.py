import rules

from dino.synczones.models import Zone
from dino.tenants.models import Membership, PermissionLevels


@rules.predicate
def is_zone_tenant_member(user, zone):
    if isinstance(zone, str):
        zone = Zone.objects.get(pk=zone)

    return zone.tenants.filter(users=user).exists()


@rules.predicate
def is_zone_tenant_admin(user, zone):
    if not zone:
        return is_any_tenant_admin(user)
    if isinstance(zone, str):
        zone = Zone.objects.get(pk=zone)

    return Membership.objects.filter(
        user=user,
        level=PermissionLevels.ADMIN,
        tenant__in=zone.tenants.all(),
    ).exists()


@rules.predicate
def is_any_tenant_admin(user):
    return Membership.objects.filter(user=user, level=PermissionLevels.ADMIN).exists()


is_zone_tenant_member = rules.is_authenticated & is_zone_tenant_member
is_zone_tenant_admin = rules.is_authenticated & is_zone_tenant_admin
is_any_tenant_admin = rules.is_authenticated & is_any_tenant_admin


@rules.predicate
def is_admin(user):
    return user.is_superuser


rules.add_perm('is_admin', is_admin)
rules.add_perm('tenants.list_zones', rules.is_authenticated)
rules.add_perm('tenants.view_zone', is_admin | is_zone_tenant_member)
rules.add_perm('tenants.delete_zone', is_admin | is_zone_tenant_admin)
rules.add_perm('tenants.create_zone', is_admin | is_any_tenant_admin)
rules.add_perm('tenants.create_record', is_admin | is_zone_tenant_member)
rules.add_perm('tenants.delete_record', is_admin | is_zone_tenant_member)
rules.add_perm('tenants.edit_record', is_admin | is_zone_tenant_member)
