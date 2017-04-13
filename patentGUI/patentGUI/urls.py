"""patentGUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from invalidators import views

urlpatterns = [
	url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.index, name='index'),
    url(r'^search/(?P<patentId>\w+)/$', views.search, name='search'),
    url(r'^stats/$', views.stats, name='stats'),
    url(r'^predict/$', views.predict, name='predict'),
    url(r'^description/$', views.description, name='description'),
    url(r'^getText/$', views.getText, name='getText'),
]

