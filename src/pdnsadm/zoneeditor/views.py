from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import RegexValidator, URLValidator
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from pdnsadm.common.views import DeleteConfirmView
from pdnsadm.pdns_api import PDNSError, PDNSNotFoundException, pdns


class PDNSDataView():
    """ provide filtering and basic context for objects w/o a database """
    filter_properties = []
    max_objects = 20

    class SearchForm(forms.Form):
        q = forms.CharField(max_length=100, label="Search", required=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PDNSDataView.SearchForm(initial={'q': self.request.GET.get('q')})
        objects = self.get_final_objects()
        context['objects'] = objects[:self.max_objects]
        context['count_all'] = len(objects)
        context['count_shown'] = len(context['objects'])
        return context

    def get_final_objects(self):
        q = self.request.GET.get('q')

        if q:
            return [
                o for o in self.get_objects()
                if any(
                    q in (o.get(p) if isinstance(o, dict) else getattr(o, p))
                    for p in self.filter_properties
                )
            ]
        else:
            return self.get_objects()


class ZoneListView(PDNSDataView, LoginRequiredMixin, TemplateView):
    template_name = "zoneeditor/zone_list.html"
    filter_properties = ['name']

    def get_objects(self):
        return pdns().get_zones()


class ZoneNameValidator(RegexValidator):
    regex = fr'^{URLValidator.hostname_re}{URLValidator.domain_re}{URLValidator.tld_re}\Z'


class ZoneCreateForm(forms.Form):
    name = forms.CharField(validators=(ZoneNameValidator(),))

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.endswith('.'):
            name = name + '.'
        return name

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
        except PDNSError as e:
            self.add_error(None, f'PowerDNS error: {e.message}')


class ZoneCreateView(LoginRequiredMixin, FormView):
    template_name = "zoneeditor/zone_create.html"
    form_class = ZoneCreateForm

    def get_success_url(self):
        name = self.form.cleaned_data['name']
        return reverse('zoneeditor:zone_detail', kwargs={'zone': name})

    def form_valid(self, form):
        self.form = form  # give get_success_url access
        return super().form_valid(form)


class ZoneDetailMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone_name'] = self.zone_name
        return context

    @property
    def zone_name(self):
        return self.kwargs['zone']


class ZoneRecordsView(PDNSDataView, ZoneDetailMixin, LoginRequiredMixin, TemplateView):
    template_name = "zoneeditor/zone_records.html"
    filter_properties = ['name']

    def get_objects(self):
        try:
            return pdns().get_records(self.zone_name)
        except PDNSNotFoundException:
            raise Http404()


class ZoneDeleteView(DeleteConfirmView, LoginRequiredMixin):
    redirect_url = reverse_lazy('zoneeditor:zone_list')

    def delete_entity(self, pk):
        pdns().delete_zone(pk)


RECORD_TYPES = [(t, t) for t in [
    'A',
    'AAAA',
    'CNAME',
    'MX',
]]

class RecordCreateForm(forms.Form):
    name = forms.CharField()
    rtype = forms.ChoiceField(choices=RECORD_TYPES, initial='A', label='Record Type')
    ttl = forms.IntegerField(min_value=1, initial=300, label='TTL')
    content = forms.CharField()

    def __init__(self, zone_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zone_name = zone_name

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.endswith(self.zone_name):
            name = f'{name}.{self.zone_name}'
        return name

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
            self.add_error(None, f'PowerDNS error: {e.message}')


class RecordCreateView(ZoneDetailMixin, LoginRequiredMixin, FormView):
    template_name = "zoneeditor/record_create.html"
    form_class = RecordCreateForm

    def get_success_url(self):
        return reverse('zoneeditor:zone_detail', kwargs={'zone': self.zone_name})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['zone_name'] = self.zone_name
        return kwargs
