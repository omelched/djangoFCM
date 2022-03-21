from django.urls import path

from djangoFCM.views.admin.metadata import MetadataJsonView
from djangoFCM.views.admin.fetcher import DataFetcherJsonView

urlpatterns = (
    path("admin/metadata",  MetadataJsonView.as_view(), name='metadata'),
    path("admin/fetcher",  DataFetcherJsonView.as_view(), name='fetcher'),
)