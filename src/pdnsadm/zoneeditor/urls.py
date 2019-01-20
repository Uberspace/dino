from django.urls import path
from django.views.generic.base import RedirectView

import pdnsadm.zoneeditor.views as views

app_name = 'zoneeditor'
urlpatterns = [
    path('zones', views.ZoneListView.as_view(), name="zone_list"),
    path('zones/create', views.ZoneCreateView.as_view(), name="zone_create"),
    path('zones/<zone>', RedirectView.as_view(pattern_name='zoneeditor:zone_records', permanent=False), name="zone_detail"),
    path('zones/<zone>/records', views.ZoneRecordsView.as_view(), name="zone_records"),
]
