import rules


@rules.predicate
def is_tenant_member(user, tenant):
    return tenant.users.filter(pk=user.pk).exists()

@rules.predicate
def is_zone_tenant_member(user, zone):
    from pdnsadm.synczones.models import Zone

    if isinstance(zone, str):
        zone = Zone.objects.get(pk=zone)

    return zone.tenants.filter(users=user).exists()

is_zone_tenant_member = rules.is_authenticated & is_zone_tenant_member

@rules.predicate
def is_admin(user):
    return user.is_superuser


rules.add_perm('tenants.list_zones', rules.is_authenticated)
rules.add_perm('tenants.view_zone', is_admin | is_zone_tenant_member)
rules.add_perm('tenants.delete_zone', is_admin)
rules.add_perm('tenants.create_zone', is_admin)
rules.add_perm('tenants.create_record', is_admin | is_zone_tenant_member)
rules.add_perm('tenants.delete_record', is_admin | is_zone_tenant_member)
