import datetime

from django.core.urlresolvers import reverse

from djangorestframework.mixins import ResponseMixin
from djangorestframework.response import Response
from djangorestframework.views import View

from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.restapi.renderers import RENDERERS

from lizard_map.daterange import default_start
from lizard_map.daterange import default_end

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

class JdbcRestView(View):
    jdbc_source_slug = None
    allowed_methods = ('GET',)
    
    @property
    def jdbc_source(self):
        return JdbcSource.objects.get(slug=self.jdbc_source_slug)

class HomeView(JdbcRestView):
    def get(self, request):
        filtertree = self.jdbc_source.get_filter_tree()

        def clean_filter_tree(filtertree):
            for item in filtertree:
                # Not needed
                del item["parentid"]

                if item["children"]:
                    # Item is a node
                    clean_filter_tree(item["children"])
                    # Not needed
                    del item["id"]
                    del item["name"]
                    del item["url"]
                else:
                    # Item is a leaf
                    del item["children"]
                    item["url"] = reverse('filter_view', kwargs={'filter_id': item["id"]})

                    # Rename
                    item["filter_id"] = item["id"]
                    del item["id"]
                    item["filter_name"] = item["name"]
                    del item["name"]

        clean_filter_tree(filtertree)

        return Response(200, {'filter_tree': filtertree })

    
class FilterView(JdbcRestView):
    def get(self, request, filter_id):
        parameters = self.jdbc_source.get_named_parameters(filter_id)

        for parameter in parameters:
            # These are superfluous
            del parameter["filter_id"]
            del parameter["filter_name"]

            # Add url
            parameter["url"] = reverse('parameter_view',
                                       kwargs={'filter_id': filter_id,
                                               'parameter_id': parameter["parameterid"]})

        return Response(200, {
                'filter_id': filter_id,
                'filter_url': reverse('filter_view', kwargs={'filter_id': filter_id}),
                'parameters': parameters
                })

class ParameterView(JdbcRestView):
    def get(self, request, filter_id, parameter_id):
        locations = self.jdbc_source.get_locations(filter_id, parameter_id)

        for location in locations:
            # Add url
            location["url"] = reverse('location_view',
                                      kwargs={'filter_id': filter_id,
                                              'parameter_id': parameter_id,
                                              'location_id': location["locationid"]})

        return Response(200, {
                'filter_id': filter_id,
                'filter_url': reverse('filter_view', kwargs={'filter_id': filter_id}),
                'parameter_id': parameter_id,
                'parameter_url': reverse('parameter_view', kwargs={'filter_id': filter_id,
                                                                   'parameter_id': parameter_id}),
                'locations': locations
                })

class LocationView(JdbcRestView):
    def get(self, request, filter_id, parameter_id, location_id):
        start_date, end_date = start_end_dates(request)

        timeseries = self.jdbc_source.get_timeseries(filter_id, location_id, parameter_id, start_date, end_date)

        return Response(200, {
                'filter_id': filter_id,
                'filter_url': reverse('filter_view', kwargs={'filter_id': filter_id}),
                'parameter_id': parameter_id,
                'parameter_url': reverse('parameter_view', kwargs={'filter_id': filter_id,
                                                                   'parameter_id': parameter_id}),
                'location_id': location_id,
                'location_url': reverse('location_view', kwargs={'filter_id': filter_id,
                                                                 'parameter_id': parameter_id,
                                                                 'location_id': location_id}),
                'timeseries': timeseries
                })
        
