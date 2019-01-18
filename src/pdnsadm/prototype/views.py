import random

from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator

import powerdns


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


class NoModelListViewMixin():
    paginate_by = 10
    context_paginator_name = 'paginator'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_paginator_name] = self._paginator
        context[self.context_object_name] = self.current_page
        return context

    @property
    def current_page(self):
        return self._paginator.page(self.request.GET.get('page', 1))

    @property
    def _paginator(self):
        return Paginator(self.get_objects(), self.paginate_by)

    def get_objects(self):
        raise NotImplementedError()


class HomePageView(NoModelListViewMixin, TemplateView):
    template_name = "prototype/home.html"

    def get_objects(self):
        return pdns().server.zones
