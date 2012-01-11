from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from lizard_fewsjdbc.restapi import views

def urls(jdbc_source_slug=None):
    _jdbc_filter = r'(?P<filter_id>[^/]+)/'
    _jdbc_filter_parameter = (_jdbc_filter+r'(?P<parameter_id>[^/]+)/')
    _jdbc_filter_parameter_location = (_jdbc_filter_parameter+
                                       r'(?P<location_id>[^/]+)/')

    return patterns('',
        url(r'^$',
            views.HomeView.as_view(jdbc_source_slug=jdbc_source_slug),
            name='home_view'),
        url(r'^%s$' % _jdbc_filter,
            views.FilterView.as_view(jdbc_source_slug=jdbc_source_slug),
            name='filter_view'),
        url(r'^%s$' % _jdbc_filter_parameter,
            views.ParameterView.as_view(jdbc_source_slug=jdbc_source_slug),
            name='parameter_view'),
        url(r'^%s$' % _jdbc_filter_parameter_location,
            views.LocationView.as_view(jdbc_source_slug=jdbc_source_slug),
            name='location_view'),
        )
