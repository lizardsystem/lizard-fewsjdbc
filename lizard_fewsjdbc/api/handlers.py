# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
"""
Handlers for the REST api provided through django-piston.


"""
import csv
import datetime
import time
import urllib

from django.http import HttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from piston.handler import BaseHandler
from piston.utils import rc
from lizard_map.api.handlers import documentation
from lizard_map.daterange import default_start
from lizard_map.daterange import default_end

from lizard_fewsjdbc.layers import FewsJdbc
from lizard_fewsjdbc.models import JdbcSource

FILTER_URL_NAME = 'api_jdbc_filters'
PARAMETER_URL_NAME = 'api_jdbc_parameters'
LOCATION_URL_NAME = 'api_jdbc_locations'
TIMESERIE_URL_NAME = 'api_jdbc_timeseries'
GET_PARAM_DATE_FORMAT = '%Y-%m-%d'


def start_end_dates(request):
    start_date = datetime.datetime.now() + default_start()
    end_date = datetime.datetime.now() + default_end()
    if 'period' in request.GET:
        end_date = datetime.datetime.now() + datetime.timedelta(hours=1)
        # ^^^ Now plus padding.
        days_before = int(request.GET['period'])
        start_date = datetime.datetime.now() - datetime.timedelta(days_before)
    else:
        if 'start' in request.GET:
            try:
                date = time.strptime(request.GET['start'],
                                     GET_PARAM_DATE_FORMAT)
                start_date = datetime.date(
                    year=date.tm_year,
                    month=date.tm_mon,
                    day=date.tm_mday)
            except ValueError:
                pass
        if 'end' in request.GET:
            try:
                date = time.strptime(request.GET['end'], GET_PARAM_DATE_FORMAT)
                end_date = datetime.date(
                    year=date.tm_year,
                    month=date.tm_mon,
                    day=date.tm_mday)
            except ValueError:
                pass

    if start_date > end_date:
        # Yes, Reinout made that happen...
        raise ValueError("Start date %s is later than end date %s ..." % (
                start_date, end_date))
    return start_date, end_date


class JdbcHandler(BaseHandler):
    """Show info on available FEWS jdbcs."""
    allowed_methods = ('GET',)
    model = JdbcSource

    def read(self, request):
        result = {}
        result['info'] = documentation(self.__class__)
        data = []
        for jdbc_source in JdbcSource.objects.all():
            url = request.build_absolute_uri(
                reverse(FILTER_URL_NAME,
                        kwargs={'jdbc_source_slug': jdbc_source.slug}))
            data.append({'title': jdbc_source.name,
                         'url': url})
        result['data'] = data
        return result


class FilterHandler(BaseHandler):
    """Show available filters for a FEWS jdbc.

    The returned structure is nested as filters are hierarchical.
    Folders have a ``title`` and a ``children`` key, end nodes with
    data have ``title`` and ``url``.  The URL points at the available
    parameters for that filter.

    """
    allowed_methods = ('GET',)

    def _return_data(self, tree, request, jdbc_source_slug):
        """Return tree filtered to what we need."""
        result = []
        for item in tree:
            node = {}
            node['title'] = item['name']
            if not 'children' in item:
                # Some jdbc connection error.
                result = [node]
                return result
            if item['children']:
                # We're a folder.
                node['children'] = self._return_data(
                    item['children'], request, jdbc_source_slug)
            else:
                # We're an end node.
                safe_id = urllib.quote(item['id'], '')
                # There can be slashes in the id, so we quote it.  The
                # empty string means "no safe characters, like '/'".
                url = request.build_absolute_uri(
                    reverse(
                        PARAMETER_URL_NAME,
                        kwargs={'jdbc_source_slug': jdbc_source_slug,
                                'filter_id': safe_id}))
                node['url'] = url
            result.append(node)
        return result

    def read(self, request, jdbc_source_slug):
        result = {}
        result['info'] = documentation(self.__class__)
        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)
        result['data'] = self._return_data(
            jdbc_source.get_filter_tree(),
            request, jdbc_source_slug)
        return result


class ParameterHandler(BaseHandler):
    """Show a filter's available parameters."""
    allowed_methods = ('GET',)

    def read(self, request, jdbc_source_slug, filter_id):
        safe_filter_id = filter_id
        filter_id = urllib.unquote(filter_id)
        result = {}
        result['info'] = documentation(self.__class__)
        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)
        data = []
        for parameter in jdbc_source.get_named_parameters(
            filter_id):
            safe_parameter_id = urllib.quote(parameter['parameterid'], '')
            url = request.build_absolute_uri(
                reverse(
                    LOCATION_URL_NAME,
                    kwargs={'jdbc_source_slug': jdbc_source_slug,
                            'filter_id': safe_filter_id,
                            'parameter_id': safe_parameter_id}))
            data.append({'title': parameter['parameter'],
                         'url': url})
        result['data'] = data
        return result


class LocationHandler(BaseHandler):
    """Show a parameter's locations."""
    allowed_methods = ('GET',)

    def read(self, request, jdbc_source_slug, filter_id, parameter_id):
        safe_filter_id = filter_id
        filter_id = urllib.unquote(filter_id)
        safe_parameter_id = parameter_id
        parameter_id = urllib.unquote(parameter_id)
        result = {}
        result['info'] = documentation(self.__class__)
        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)
        data = []
        for location in jdbc_source.get_locations(filter_id, parameter_id):
            safe_location_id = urllib.quote(location['locationid'], '')
             # TODO: add geojson coordinates!!!
            url = request.build_absolute_uri(
                reverse(
                    TIMESERIE_URL_NAME,
                    kwargs={'jdbc_source_slug': jdbc_source_slug,
                            'filter_id': safe_filter_id,
                            'parameter_id': safe_parameter_id,
                            'location_id': safe_location_id}))
            data.append({'title': location['location'],
                         'url': url})
        result['data'] = data
        return result


class TimeserieHandler(BaseHandler):
    """Show a location's timeseries data.


    This is the main endpoint of the jdbc FEWS data.  The data
    returned can be big, depending on the date range and the amount of
    data per time period.

    See the 'alternative_representations' for urls for csv/png/html
    output.

    Start/end dates can be given as extra GET parameters by adding
    ``?start=yyyy-mm-dd&end=yyyy-mm-dd`` to the URL.

    An alternative is to pass a ``?period=7`` period parameter.  The
    start date is set the given amount of days earlier than the
    default end date (often "today").  The period parameter takes
    precedence over the start/end date parameters.

    You can pass 'height' and 'width' GET parameters to the png
    representation url get the correct image size (in pixels).

    """
    allowed_methods = ('GET',)

    def read(self, request,
             jdbc_source_slug, filter_id, parameter_id, location_id):
        safe_filter_id = filter_id
        filter_id = urllib.unquote(filter_id)
        safe_parameter_id = parameter_id
        parameter_id = urllib.unquote(parameter_id)
        safe_location_id = location_id
        location_id = urllib.unquote(location_id)
        result = {}
        result['info'] = documentation(self.__class__)

        alternative_representations = []
        for format in ('csv', 'png', 'html'):
            url = request.build_absolute_uri(
                reverse(
                    TIMESERIE_URL_NAME + '_' + format,
                    kwargs={'jdbc_source_slug': jdbc_source_slug,
                            'filter_id': safe_filter_id,
                            'parameter_id': safe_parameter_id,
                            'location_id': safe_location_id}))
            alternative_representations.append(
                {'url': url,
                 'format': format})
        result['alternative_representations'] = alternative_representations

        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)
        start_date, end_date = start_end_dates(request)
        data = jdbc_source.get_timeseries(
            filter_id, location_id, parameter_id,
            start_date, end_date)
        if not data:
            response = rc.NOT_FOUND
            response.write(
                "No data found for this filter/parameter/location combination")
            return response
        result['data'] = data

        # TODO: fix this parameter_name, get_parameter_name does not exist

        # result['parameter_name'] = jdbc_source.get_parameter_name(
        # parameter_id)

        result['parameter_name'] = parameter_id
        # ^^^ Not sure this is a great place to set this, but we need it for
        # now.

        return result


class TimeserieCsvHandler(TimeserieHandler):
    """Specific handler for csv output: emitter can't set response headers."""

    def read(self, request,
             jdbc_source_slug, filter_id, parameter_id, location_id):
        result = TimeserieHandler.read(
            self, request,
            jdbc_source_slug, filter_id, parameter_id, location_id)
        if isinstance(result, HttpResponse):
            # Probably 404 response.  It would be handier if piston would
            # handle 404 exceptions more properly.
            return result

        headers = ['time', result['parameter_name']]
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=timeseries.csv'

        writer = csv.writer(response)
        writer.writerow(headers)
        for timeserie in result['data']:
            row = []
            for key in ('time', 'value'):
                row.append(timeserie[key])
            writer.writerow(row)
        return response


class TimeseriePngHandler(BaseHandler):
    """Show a location's timeseries data as a png image.

    Start/end dates can be given as extra GET parameters by adding
    ``?start=yyyy-mm-dd&end=yyyy-mm-dd`` to the URL.

    """
    allowed_methods = ('GET',)

    def read(self, request,
             jdbc_source_slug, filter_id, parameter_id, location_id):
        filter_id = urllib.unquote(filter_id)
        parameter_id = urllib.unquote(parameter_id)
        location_id = urllib.unquote(location_id)

        layer_arguments = {
            'slug': jdbc_source_slug,
            'filter': filter_id,
            'parameter': parameter_id,
            }
        adapter = FewsJdbc(None, layer_arguments=layer_arguments)
        identifiers = [{'location': location_id}]
        start_date, end_date = start_end_dates(request)
        height = request.GET.get('height', 500)
        width = request.GET.get('width', 500)
        try:
            result = adapter.image(identifiers,
                                   start_date,
                                   end_date,
                                   height=height,
                                   width=width,
                                   raise_404_if_empty=True)
            return result
        except Http404:
            response = rc.NOT_FOUND
            response.write(
                "No data found for this filter/parameter/location combination")
            return response
