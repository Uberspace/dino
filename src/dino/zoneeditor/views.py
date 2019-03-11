from django import forms
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core import signing
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.paginator import Paginator
from django.core.validators import RegexValidator, URLValidator
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rules.contrib.views import PermissionRequiredMixin

from dino.common.fields import SignedHiddenField
from dino.common.views import DeleteConfirmView
from dino.pdns_api import PDNSError, PDNSNotFoundException, pdns
from dino.synczones.models import Zone
from dino.tenants.models import PermissionLevels, Tenant


class SearchForm(forms.Form):
    q = forms.CharField(max_length=100, label=_("Search"), required=False, widget=forms.TextInput(attrs={'class': 'input-group-field'}))


class ZoneListView(PermissionRequiredMixin, ListView):
    permission_required = 'tenants.list_zones'
    template_name = "zoneeditor/zone_list.html"
    model = Zone
    paginate_by = 20

    def __init__(self, **kwargs):
        self._zones_refreshed = False
        return super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        if self.query:
            name = self.query.rstrip('.') + '.'

            if self.get_queryset().filter(name=name).exists():
                return HttpResponseRedirect(reverse('zoneeditor:zone_detail', kwargs={'zone': name}))

        return super().get(request, *args, **kwargs)

    @property
    def query(self):
        return self.request.GET.get('q')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(initial={'q': self.query})
        return context

    def _refresh_zones(self):
        if not self._zones_refreshed:
            # TODO: doing this every time the list is loaded is a bad idea
            Zone.import_from_powerdns(pdns().get_zones())
            self._zones_refreshed = True

    def get_queryset(self):
        self._refresh_zones()

        zones = Zone.objects.all().order_by('name')

        if not self.request.user.is_superuser:
            zones = zones.filter(tenants__users=self.request.user)

        if self.query:
            zones = zones.filter(name__icontains=self.query)

        return zones


class ZoneNameValidator(RegexValidator):
    unanchored_regex = fr'{URLValidator.hostname_re}{URLValidator.domain_re}{URLValidator.tld_re}'
    regex = fr'^{unanchored_regex}\Z'


class RecordNameValidator(RegexValidator):
    regex = fr'^(@\Z|{URLValidator.hostname_re}({URLValidator.domain_re}{URLValidator.tld_re})?)\Z'


class ZoneCreateForm(forms.Form):
    name = forms.CharField(validators=(ZoneNameValidator(),))
    tenants = forms.ModelMultipleChoiceField(queryset=Tenant.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.has_perm('is_admin'):
                self.fields['tenants'].queryset = Tenant.objects.all()
            else:
                # tenants.create_zone
                self.fields['tenants'].queryset = self.user.tenants.filter(membership__level=PermissionLevels.ADMIN)

        if self.fields['tenants'].queryset.count() == 0:
            self.fields['tenants'].widget = forms.HiddenInput()

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.endswith('.'):
            name = name + '.'
        return name

    def clean_tenants(self):
        if self.user and not self.user.has_perm('is_admin') and self.cleaned_data['tenants'].count() == 0:
            raise forms.ValidationError(_('Please choose a tenant, as you will otherwise not be able to access the new zone after creation.'))

        return self.cleaned_data['tenants']

    def _post_clean(self):
        if not self.errors:
            self.create_zone()

    def create_zone(self):
        try:
            pdns().create_zone(
                name=self.cleaned_data['name'],
                kind=settings.ZONE_DEFAULT_KIND,
                nameservers=settings.ZONE_DEFAULT_NAMESERVERS,
            )

            zone = Zone.objects.create(name=self.cleaned_data['name'])
            for tenant in self.cleaned_data['tenants']:
                tenant.zones.add(zone)
        except PDNSError as e:
            self.add_error(None, _('PowerDNS error: {}').format(e.message))


class ZoneCreateView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = 'tenants.create_zone'
    template_name = "zoneeditor/zone_create.html"
    form_class = ZoneCreateForm

    def get_success_url(self):
        name = self.form.cleaned_data['name']
        return reverse('zoneeditor:zone_detail', kwargs={'zone': name})

    def get_success_message(self, cleaned_data):
        return _('Zone {} has been created.').format(cleaned_data["name"])

    def form_valid(self, form):
        self.form = form  # give get_success_url access
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ZoneDetailMixin(PermissionRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone_name'] = self.zone_name
        return context

    def get_permission_object(self):
        return self.zone_name

    @property
    def zone_name(self):
        return self.kwargs['zone']


class ZoneRecordsView(ZoneDetailMixin, TemplateView):
    permission_required = 'tenants.view_zone'
    template_name = "zoneeditor/zone_records.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(initial={'q': self.request.GET.get('q')})
        context['object_list'] = self.current_page.object_list
        context['page_obj'] = self.current_page
        context['paginator'] = self._paginator
        return context

    @property
    def current_page(self):
        return self._paginator.page(self.request.GET.get('page', 1))

    @property
    def _paginator(self):
        return Paginator(self.filtered_records, self.paginate_by)

    @cached_property
    def filtered_records(self):
        q = self.request.GET.get('q')

        try:
            records = pdns().get_records(self.zone_name)
        except PDNSNotFoundException:
            raise Http404()

        if q:
            q = q.lower()
            is_apex_search = (q == '@')

            return [
                r for r in records
                if
                    q.upper() == r['rtype'] or
                    q in r['name'].lower() or
                    (is_apex_search and r['name'] == self.zone_name)
            ]
        else:
            return records


class ZoneDeleteView(PermissionRequiredMixin, DeleteConfirmView):
    permission_required = 'tenants.delete_zone'
    redirect_url = reverse_lazy('zoneeditor:zone_list')

    def delete_entity(self, pk):
        if not self.request.user.has_perm(self.permission_required, pk):
            raise PermissionDenied()

        pdns().delete_zone(pk)
        Zone.objects.filter(name=pk).delete()


class RecordForm(forms.Form):
    name = forms.CharField(validators=(RecordNameValidator(),), required=False)
    rtype = forms.ChoiceField(choices=settings.RECORD_TYPES, initial='A', label=_('Type'))
    ttl = forms.IntegerField(min_value=1, initial=300, label=_('TTL'))
    content = forms.CharField(max_length=65536)

    def __init__(self, zone_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zone_name = zone_name

    def clean_name(self):
        name = self.cleaned_data['name']

        if not name or name == '@' or name.strip('.') == self.zone_name.strip('.'):
            # apex/root record
            name = self.zone_name
        else:
            if not name.endswith('.'):
                name = name + '.'
            if not name.endswith('.' + self.zone_name):
                name = f'{name}{self.zone_name}'

        return name


class RecordCreateForm(RecordForm, forms.Form):
    def _post_clean(self):
        if not self.errors:
            self.create_record()

    def create_record(self):
        try:
            pdns().create_record(
                zone=self.zone_name,
                name=self.cleaned_data['name'],
                rtype=self.cleaned_data['rtype'],
                ttl=self.cleaned_data['ttl'],
                content=self.cleaned_data['content'],
            )
        except PDNSError as e:
            self.add_error(None, _('PowerDNS error: {}').format(e.message))


class RecordEditForm(RecordForm, forms.Form):
    identifier = SignedHiddenField()

    def _post_clean(self):
        if not self.errors:
            self.update_record()

    @property
    def old_record(self):
        r = self.cleaned_data['identifier'].copy()
        r.pop('zone', None)
        return r

    @property
    def new_record(self):
        return {
            k: v for k, v in self.cleaned_data.items()
            if k in ['name', 'rtype', 'ttl', 'content']
        }

    def _create(self, record):
        pdns().create_record(zone=self.zone_name, **record)

    def _delete(self, record):
        record = record.copy()
        record.pop('ttl', None)
        pdns().delete_record(zone=self.zone_name, **record)

    def update_record(self):
        if self.new_record == self.old_record:
            return

        if self.new_record['rtype'] == self.old_record['rtype'] and \
                self.new_record['name'] == self.old_record['name']:
            # TODO: replace cleanely in API
            pass

        try:
            self._create(self.new_record)
        except PDNSError as e_new:
            self.add_error(None, _('Could not create new record.') + ' ' + _('PowerDNS error: {}').format(e_new.message))
            return

        try:
            self._delete(self.old_record)
        except PDNSError as e:
            self.add_error(None, _('Could not delete old record.') + ' ' + _('PowerDNS error: {}').format(e.message))

            try:
                self._delete(self.new_record)
            except PDNSError as e:
                self.add_error(None, _('Could not delete new record; it may be duplicated now.') + ' ' + _('PowerDNS error: {}').format(e.message))


class RecordCreateView(ZoneDetailMixin, SuccessMessageMixin, FormView):
    permission_required = 'tenants.create_record'
    template_name = "zoneeditor/record_create.html"
    form_class = RecordCreateForm

    def get_success_url(self):
        return reverse('zoneeditor:zone_detail', kwargs={'zone': self.zone_name})

    def get_success_message(self, cleaned_data):
        return _('Record {rtype} {name} has been created.').format(rtype=cleaned_data["rtype"], name=cleaned_data["name"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['zone_name'] = self.zone_name
        return kwargs


class RecordEditView(ZoneDetailMixin, SuccessMessageMixin, FormView):
    permission_required = 'tenants.edit_record'
    template_name = "zoneeditor/record_edit.html"
    form_class = RecordEditForm

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    def get_success_url(self):
        return reverse('zoneeditor:zone_detail', kwargs={'zone': self.zone_name})

    def get_success_message(self, cleaned_data):
        return _('Record {rtype} {name} has been saved.').format(rtype=cleaned_data["rtype"], name=cleaned_data["name"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['zone_name'] = self.zone_name
        if kwargs['data'].keys() - {'csrfmiddlewaretoken'} == {'identifier'}:
            # initial submit from record list: fill fields with old record data
            # and make django belive that there never was a submit, to skip
            # and actual record editing validation.
            kwargs['initial'] = {
                'identifier': kwargs['data']['identifier'],
                **signing.loads(kwargs['data']['identifier']),
            }
            kwargs['data'] = None
            kwargs['files'] = None
        return kwargs


class RecordDeleteView(ZoneDetailMixin, DeleteConfirmView):
    permission_required = 'tenants.delete_record'

    def get_display_identifier(self, rr):
        return f"{rr['rtype']} {rr['name']} {rr['content']}"

    def delete_entity(self, rr):
        # permission check is done based on kwarg, so make sure we use the same for deletion.
        # even without this check the delete would eventually fail because the client tries
        # to delete "www.example.com." out of zone "example.org.", which only makes sense
        # for every special constellations (e.g. "customer.com.internal.proxy").
        if rr['zone'] != self.kwargs['zone']:
            raise SuspiciousOperation('zone name in kwargs does not match zone name in payload.')
        pdns().delete_record(rr['zone'], rr['name'], rr['rtype'], rr['content'])

    def get_redirect_url(self, rr):
        return reverse('zoneeditor:zone_records', kwargs={'zone': rr['zone']})
