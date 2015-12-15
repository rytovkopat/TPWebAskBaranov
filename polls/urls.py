from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^hot', views.index, {'order': 'hot'}, name='hot'),
    url(r'^newest', views.index, {'order':'newest'}, name="newest"),
    url(r'^question/(?P<question_id>\d+)', views.question, name="question"),
    url(r'^tag/(?P<tag>[A-Za-z0-9-]+)/$', views.tag, name="tag"),
    url(r'^ask', views.ask, name='ask'),
    url(r'^login', views.login, name='login'),
    url(r'^signup', views.register, name='register'),
    url(r'^logout', views.logout, name="logout"),
    url(r'^like', views.like, name='like'),
    url(r'^correct/$', views.set_correct, name='correct'),
]
