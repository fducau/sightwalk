from django.conf.urls import url

from . import views

app_name = 'paths'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^shortest/$', views.shortest, name='shortest'),
    url(r'^interesting/$', views.interesting, name='interesting'),
    url(r'^score/$', views.score, name='score'),
]