from django.conf.urls.defaults import *
from piston.resource import Resource

from lizard_fewsjdbc.api.handlers import JdbcHandler
from lizard_fewsjdbc.api.handlers import FilterHandler
from lizard_fewsjdbc.api.handlers import ParameterHandler
from lizard_fewsjdbc.api.handlers import LocationHandler
from lizard_fewsjdbc.api.handlers import TimeserieHandler
from lizard_fewsjdbc.layers import JDBC_API_URL_NAME
from lizard_fewsjdbc.api.handlers import FILTER_URL_NAME
from lizard_fewsjdbc.api.handlers import PARAMETER_URL_NAME
from lizard_fewsjdbc.api.handlers import LOCATION_URL_NAME
from lizard_fewsjdbc.api.handlers import TIMESERIE_URL_NAME

jdbc_handler = Resource(JdbcHandler)
filter_handler = Resource(FilterHandler)
parameter_handler = Resource(ParameterHandler)
location_handler = Resource(LocationHandler)
timeserie_handler = Resource(TimeserieHandler)

urlpatterns = patterns(
    '',
    url(r'^(?P<jdbc_source_slug>[^/]+)/(?P<filter_id>[^/]+)/(?P<parameter_id>[^/]+)/(?P<location_id>[^/]+)/$', 
        timeserie_handler, 
        name=TIMESERIE_URL_NAME),
    url(r'^(?P<jdbc_source_slug>[^/]+)/(?P<filter_id>[^/]+)/(?P<parameter_id>[^/]+)/$', 
        location_handler, 
        name=LOCATION_URL_NAME),
    url(r'^(?P<jdbc_source_slug>[^/]+)/(?P<filter_id>[^/]+)/$', 
        parameter_handler, 
        name=PARAMETER_URL_NAME),
    url(r'^(?P<jdbc_source_slug>[^/]+)/$', 
        filter_handler, 
        name=FILTER_URL_NAME),
    url(r'^$',
        jdbc_handler, 
        name=JDBC_API_URL_NAME),
    )
