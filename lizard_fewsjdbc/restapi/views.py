import time
import datetime
import logging

from django.core.urlresolvers import reverse

from djangorestframework.response import Response
from djangorestframework.views import View

from lizard_fewsjdbc.restapi.renderers import RENDERERS
from lizard_fewsjdbc.models import JdbcSource

from lizard_map.daterange import default_start
from lizard_map.daterange import default_end

GET_PARAM_DATE_FORMAT = '%Y-%m-%d'

logger = logging.getLogger(__name__)


def start_end_dates(request):
    start_date = default_start(datetime.datetime.now())
    end_date = default_end(datetime.datetime.now())

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


class JdbcRestAPIView(View):
    # Override the following in the site that is using the API.
    jdbc_source_slug = None

    title = "Lizard FewsJDBC REST API"
    name = "Lizard FewsJDBC REST API"
    ##

    allowed_methods = ('GET', 'OPTIONS')
    renderers = RENDERERS

    @property
    def jdbc_source(self):
        return JdbcSource.objects.get(slug=self.jdbc_source_slug)

    def get(self, request, filter_id=None,
            parameter_id=None, location_id=None):
        # These are stored so that subclasses can use them in
        # functions called by the template.
        self.filter_id = filter_id
        self.parameter_id = parameter_id
        self.location_id = location_id

        self.breadcrumblist = [('Startpunt',
                                reverse('fewsjdbc.restapi.home_view'))]
        if filter_id is None:
            return self.get_home(request)

        self.breadcrumblist.append(
            (filter_id, reverse('fewsjdbc.restapi.filter_view',
                                kwargs={'filter_id': filter_id})))
        if parameter_id is None:
            return self.get_filter(request, filter_id)

        self.breadcrumblist.append(
            (parameter_id, reverse('fewsjdbc.restapi.parameter_view',
                                   kwargs={'filter_id': filter_id,
                                           'parameter_id': parameter_id})))
        if location_id is None:
            return self.get_parameter(request, filter_id, parameter_id)

        self.breadcrumblist.append(
            (location_id, reverse('fewsjdbc.restapi.location_view',
                                  kwargs={'filter_id': filter_id,
                                          'parameter_id': parameter_id,
                                          'location_id': location_id})))
        return self.get_location(request, filter_id, parameter_id, location_id)

    def get_home(self, request):
        filtertree = self.jdbc_source.get_filter_tree(url_name=None)
        logger.debug(filtertree)
        items = dict()

        def items_in_filter_tree(items, filtertree):
            for item in filtertree:
                if item["children"]:
                    # Item is a node
                    items_in_filter_tree(items, item["children"])
                else:
                    items[item["id"]] = reverse('fewsjdbc.restapi.filter_view',
                                                kwargs={'filter_id':
                                                            item["id"]})

        items_in_filter_tree(items, filtertree)

        return Response(200, items)

    def get_filter(self, request, filter_id):
        parameters = (self.jdbc_source.
                      get_named_parameters(filter_id, find_lowest=False))

        filter = {}
        for parameter in parameters:
            filter[parameter["parameter"]] = (
                reverse('fewsjdbc.restapi.parameter_view',
                        kwargs={'filter_id': filter_id,
                                'parameter_id': parameter["parameterid"]}))
        return Response(200, filter)

    def get_parameter(self, request, filter_id, parameter_id):
        locations = self.jdbc_source.get_locations(filter_id, parameter_id)

        parameter = {}
        for location in locations:
            parameter[location["location"]] = (
                reverse('fewsjdbc.restapi.location_view',
                        kwargs={'filter_id': filter_id,
                                'parameter_id': parameter_id,
                                'location_id': location["locationid"]}))
        return Response(200, parameter)

    def get_location(self, request, filter_id, parameter_id, location_id):
        start_date, end_date = start_end_dates(request)

        timeseries = self.jdbc_source.get_timeseries(filter_id,
                                                     location_id,
                                                     parameter_id,
                                                     start_date,
                                                     end_date)

        return Response(200, timeseries)
