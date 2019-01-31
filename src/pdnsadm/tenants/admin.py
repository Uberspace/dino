from django.contrib import admin

from .models import Membership, Tenant


class MembershipInline(admin.TabularInline):
    model = Membership
    raw_id_fields = ('user',)
    extra = 1
    verbose_name = 'Member'
    verbose_name_plural = 'Members'


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    model = Tenant
    inlines = [
        MembershipInline,
    ]
    filter_horizontal = ('zones',)
    fields = (
        'name',
        'zones',
    )
