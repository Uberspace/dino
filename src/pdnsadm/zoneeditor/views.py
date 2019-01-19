from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

from pdnsadm.pdns_api import pdns


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
        return pdns().server.zones


class ZoneRecordsView(PDNSDataView, LoginRequiredMixin, TemplateView):
    template_name = "zoneeditor/zone_records.html"
    filter_properties = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone_name'] = self.zone_name
        return context

    @property
    def zone_name(self):
        return self.kwargs['zone'].rstrip('.') + '.'

    def get_objects(self):
        zone = pdns().server.get_zone(self.zone_name)
        return zone.records_axfr()
