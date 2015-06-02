from django.conf.urls import url
from main.views.index import index_action
from main.views.action import execute_action
from main.views.image import image_action

urlpatterns = [
    url(r'^$', index_action, name='index'),
    url(r'^action/(?P<name>[a-z\-]+)/$', execute_action, name='action'),
    url(r'^image/$', image_action, name='image'),
]