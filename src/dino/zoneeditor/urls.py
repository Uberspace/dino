from django.urls import path
from django.views.generic.base import RedirectView

import dino.zoneeditor.views as views

app_name = 'zoneeditor'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='zoneeditor:zone_list', permanent=False), name="index"),
    path('zones', views.ZoneListView.as_view(), name="zone_list"),
    path('zones/create', views.ZoneCreateView.as_view(), name="zone_create"),
    path('zones/delete', views.ZoneDeleteView.as_view(), name="zone_delete"),
    path('zones/<zone>', RedirectView.as_view(pattern_name='zoneeditor:zone_records', permanent=False), name="zone_detail"),
    path('zones/<zone>/records', views.ZoneRecordsView.as_view(), name="zone_records"),
    path('zones/<zone>/records/create', views.RecordCreateView.as_view(), name="zone_record_create"),
    path('zones/<zone>/records/delete', views.RecordDeleteView.as_view(), name="zone_record_delete"),
    path('zones/<zone>/records/edit', views.RecordEditView.as_view(), name="zone_record_edit"),
]
