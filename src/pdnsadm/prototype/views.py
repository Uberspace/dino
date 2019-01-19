import random

from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

import powerdns


def records_axfr(self):
    """Get zone's records as AXFR"""
    lines = (r.split('\t') for r in self._get(self.url + '/export')['zone'].strip().split('\n'))
    return [
        {'name': r[0], 'ttl': r[1], 'type': r[2], 'content': r[3]}
        for r in lines
    ]

powerdns.interface.PDNSZone.records_axfr = records_axfr

class pdns():
    def __init__(self):
        api_client = powerdns.PDNSApiClient(
            api_endpoint=settings.PDNS_APIURL,
            api_key=settings.PDNS_APIKEY
        )
        self.api = powerdns.PDNSEndpoint(api_client)

    @property
    def server(self):
        return self.api.servers[0]


class NoModelSearchMixin():
    filter_properties = []
    max_objects = 20

    class SearchForm(forms.Form):
        q = forms.CharField(max_length=100, label="Search", required=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = NoModelSearchMixin.SearchForm(initial={'q': self.request.GET.get('q')})
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


class HomePageView(NoModelSearchMixin, LoginRequiredMixin, TemplateView):
    template_name = "prototype/home.html"
    filter_properties = ['name']

    def get_objects(self):
        return pdns().server.zones


class ZoneView(NoModelSearchMixin, LoginRequiredMixin, TemplateView):
    template_name = "prototype/zone.html"
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
