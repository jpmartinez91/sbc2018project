from django.conf.urls import url
from views import *
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^fuentes$', Fuentes.as_view(), name='fuentes'),
    url(r'^buscador$', Buscador.as_view(), name='buscador'),
    url(r'^api_search$', SimpleSearch, name='simple'),
    url(r'^api_pais$', api_pais_search, name='pais'),
    url(r'^(?P<revista>\w+)', api_revista, name="drink"),
    url(r'^(?P<revista>\w+)', api_temas, name="drink"),
     # url(r'^api_search/(?P<revista>\[-\w]+)/$', api_revista ,name="drink"),
    # url(r'revista/(?P<revista>\d+)$', api_revista,

]
