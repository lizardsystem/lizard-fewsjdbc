from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from lizard_fewsjdbc.restapi import views


def make_patterns(subclassed_view=views.JdbcRestAPIView):
    if not issubclass(subclassed_view, views.JdbcRestAPIView):
        raise ValueError("The argument to make_patterns should be a" +
                         " class that subclasses JdbcRestAPIView.")

    _jdbc_filter = r'(?P<filter_id>[^/]+)/'
    _jdbc_filter_parameter = (_jdbc_filter + r'(?P<parameter_id>[^/]+)/')
    _jdbc_filter_parameter_location = (_jdbc_filter_parameter +
                                       r'(?P<location_id>[^/]+)/')

    return patterns(
        '',
        url(r'^$', subclassed_view.as_view(),
            name='fewsjdbc.restapi.home_view'),
        url(r'^%s$' % _jdbc_filter, subclassed_view.as_view(),
            name='fewsjdbc.restapi.filter_view'),
        url(r'^%s$' % _jdbc_filter_parameter, subclassed_view.as_view(),
            name='fewsjdbc.restapi.parameter_view'),
        url(r'^%s$' % _jdbc_filter_parameter_location,
            subclassed_view.as_view(),
            name='fewsjdbc.restapi.location_view'),
    )
