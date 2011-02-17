from django.conf.urls.defaults import *
from piston.resource import Resource

from lizard_fewsjdbc.api import emitters
from lizard_fewsjdbc.api.handlers import FILTER_URL_NAME
from lizard_fewsjdbc.api.handlers import FilterHandler
from lizard_fewsjdbc.api.handlers import JdbcHandler
from lizard_fewsjdbc.api.handlers import LOCATION_URL_NAME
from lizard_fewsjdbc.api.handlers import LocationHandler
from lizard_fewsjdbc.api.handlers import PARAMETER_URL_NAME
from lizard_fewsjdbc.api.handlers import ParameterHandler
from lizard_fewsjdbc.api.handlers import TIMESERIE_URL_NAME
from lizard_fewsjdbc.api.handlers import TimeserieHandler
from lizard_fewsjdbc.api.handlers import TimeserieCsvHandler
from lizard_fewsjdbc.api.handlers import TimeseriePngHandler
from lizard_fewsjdbc.layers import JDBC_API_URL_NAME

jdbc_handler = Resource(JdbcHandler)
filter_handler = Resource(FilterHandler)
parameter_handler = Resource(ParameterHandler)
location_handler = Resource(LocationHandler)
timeserie_handler = Resource(TimeserieHandler)
timeserie_png_handler = Resource(TimeseriePngHandler)
timeserie_csv_handler = Resource(TimeserieCsvHandler)

_jdbc = r'(?P<jdbc_source_slug>[^/]+)/'
_jdbc_filter = _jdbc + r'(?P<filter_id>[^/]+)/'
_jdbc_filter_parameter = _jdbc_filter + r'(?P<parameter_id>[^/]+)/'
_jdbc_filter_parameter_location = _jdbc_filter_parameter + r'(?P<location_id>[^/]+)/'

urlpatterns = patterns(
    '',
    url(r'^$',
        jdbc_handler, 
        name=JDBC_API_URL_NAME),
    url(r'^%s$' % _jdbc, 
        filter_handler, 
        name=FILTER_URL_NAME),
    url(r'^%s$' % _jdbc_filter, 
        parameter_handler, 
        name=PARAMETER_URL_NAME),
    url(r'^%s$' % _jdbc_filter_parameter, 
        location_handler, 
        name=LOCATION_URL_NAME),
    url(r'^%s$' % _jdbc_filter_parameter_location, 
        timeserie_handler, 
        name=TIMESERIE_URL_NAME),
    url(r'^%stimeseries.png$' % _jdbc_filter_parameter_location, 
        timeserie_png_handler,
        name=TIMESERIE_URL_NAME + '_png'),
    url(r'^%shtml/$' % _jdbc_filter_parameter_location, 
        timeserie_handler,
        {'emitter_format': 'jdbc_html_table'}, 
        name=TIMESERIE_URL_NAME + '_html'),
    url(r'^%scsv/$' % _jdbc_filter_parameter_location, 
        timeserie_csv_handler,
        name=TIMESERIE_URL_NAME + '_csv'),
    )
