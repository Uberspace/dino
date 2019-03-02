import pytest

from ...models import Membership, PermissionLevels, Tenant


@pytest.mark.django_db()
def test_membership_str(user_no_tenant):
    t = Tenant(name='Customer')
    m = Membership(
        user=user_no_tenant,
        tenant=t,
        level=PermissionLevels.ADMIN
    )
    assert 'user' in str(m)
    assert 'Customer' in str(m)


def test_tenant_str():
    t = Tenant(name='Customer')
    assert 'Customer' in str(t)
