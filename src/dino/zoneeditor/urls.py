from django.urls import include, path, register_converter
from django.views.generic.base import RedirectView

import dino.zoneeditor.views as views


class ZoneNameConverter:
    regex = views.ZoneNameValidator.unanchored_regex

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(ZoneNameConverter, 'zonename')

app_name = 'zoneeditor'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='zoneeditor:zone_list', permanent=False), name="index"),
    path('zones', views.ZoneListView.as_view(), name="zone_list"),
    path('zones/create', views.ZoneCreateView.as_view(), name="zone_create"),
    path('zones/delete', views.ZoneDeleteView.as_view(), name="zone_delete"),
    path('zones/<zonename:zone>', RedirectView.as_view(pattern_name='zoneeditor:zone_records', permanent=False), name="zone_detail"),
    path('zones/<zonename:zone>/', include([
        path('records', views.ZoneRecordsView.as_view(), name="zone_records"),
        path('records/create', views.RecordCreateView.as_view(), name="zone_record_create"),
        path('records/delete', views.RecordDeleteView.as_view(), name="zone_record_delete"),
        path('records/edit', views.RecordEditView.as_view(), name="zone_record_edit"),
    ])),
]
