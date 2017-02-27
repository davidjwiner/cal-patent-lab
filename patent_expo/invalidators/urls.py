# encoding: utf-8
from django.conf.urls import include, url
from invalidators.views import (
        FileCreateView, FileDeleteView, FileListView, predict,result
    )

urlpatterns = [
    url(r'^home/$', FileCreateView.as_view(), name='upload-new'),
    url(r'^delete/(?P<pk>\d+)$', FileDeleteView.as_view(), name='upload-delete'),
    url(r'^view/$', FileListView.as_view(), name='upload-view'),
    url(r'^predict/$', predict, name='predict'),
    url(r'^result/$', result, name = 'result'),
]
