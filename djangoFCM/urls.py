from django.urls import path
from django.contrib import admin

from djangoFCM.views.admin.metadata import MetadataJsonView
from djangoFCM.views.admin.fetcher import DataFetcherJsonView
from djangoFCM.views.admin.calendar import CalendarView

urlpatterns = (
    path("admin/metadata",  MetadataJsonView.as_view(), name='metadata'),
    path("admin/fetcher",   DataFetcherJsonView.as_view(admin_site=admin.site), name='fetcher'),
)
