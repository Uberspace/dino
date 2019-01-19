from django.urls import path

import pdnsadm.prototype.views as views

app_name = 'prototype'
urlpatterns = [
    path('', views.HomePageView.as_view(), name="zones"),
    path('zone/<zone>', views.ZoneView.as_view(), name="zone"),
]
