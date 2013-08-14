# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import logging
import requests

from lizard_fewsjdbc import models

logger = logging.getLogger(__name__)


class FewsJDBCImporter(object):

    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger("cache_fews.FewsJDBCImporter")
        else:
            self.logger = logger

    def remove_all_caches(self):
        self.logger.info("Remove caches.")
        models.FilterCache.objects.all().delete()
        models.TimeseriesCache.objects.all().delete()
        models.ParameterCache.objects.all().delete()
        models.LocationCache.objects.all().delete()

    def cache_resources(self, webrs_source):
        self.logger.debug(
            "Cache source {0}: {1}.".format(webrs_source.code,
                                            webrs_source.source_path))
        f_cached = self.cache_filters(webrs_source)
        l_cached = self.cache_locations(webrs_source)
        p_cached = self.cache_parameters(webrs_source)
        t_cached = self.cache_timeseries(webrs_source)
        if False in [f_cached, l_cached, p_cached, t_cached]:
            return False
        else:
            return True

    def cache_filters(self, webrs_source):
        """Cache filters."""
        self.logger.info("Cache filters.")
        result = requests.get(webrs_source.filters_path)
        if not result.ok:
            self.logger.error("Error on retrieving filters: HTTP "
                              "response {}.".format(result.status_code))
            return False
        for fltr in result.json:
            models.FilterCache(
                filterid=fltr.get('id'),
                name=fltr.get('name'),
                parent_id=fltr.get('parent_id')).save()
        self.logger.info("{} filters cached.".format(len(result.json)))
        return True

    def cache_locations(self, webrs_source):
        """Cache locations."""
        self.logger.info("Cache locations.")
        result = requests.get(webrs_source.locations_path)
        if not result.ok:
            self.logger.error("Error on retrieving locations: HTTP "
                              "response {}.".format(result.status_code))
            return False
        for location in result.json:
            models.LocationCache(
                locationid=location.get('id'),
                name=location.get('name'),
                short_name=location.get('short_name'),
                lng=location.get('lng'),
                lat=location.get('lat')).save()
        self.logger.info("{} locations cached.".format(len(result.json)))
        return True

    def cache_parameters(self, webrs_source):
        """Cache parameters."""
        self.logger.info("Cache parameters.")
        result = requests.get(webrs_source.parameters_path)
        if not result.ok:
            self.logger.error("Error on retrieving parameters: HTTP "
                              "response {}.".format(result.status_code))
            return False
        for parameter in result.json:
            models.ParameterCache(
                parameterid=parameter.get('id'),
                name=parameter.get('name'),
                short_name=parameter.get('short_name'),
                unit=parameter.get('unit'),
                parameter_type=parameter.get('parameter_type'),
                parameter_group=parameter.get('parameter_group')).save()
        self.logger.info("{} parameters cached.".format(len(result.json)))
        return True

    def cache_timeseries(self, webrs_source):
        """Cache timeseries."""
        self.logger.info("Cache timeseries.")
        result = requests.get(webrs_source.timeseries_path)
        if not result.ok:
            self.logger.error("Error on retrieving timeseries: HTTP "
                              "response {}.".format(result.status_code))
            return False
        for timeseries in result.json:
            filterid = timeseries.get('filter').get('id')
            locationid = timeseries.get('location').get('id')
            parameterid = timeseries.get('parameter').get('id')

            models.TimeseriesCache(
                t_filter=models.FilterCache.objects.get(pk=filterid),
                t_location=models.LocationCache.objects.get(pk=locationid),
                t_parameter=models.ParameterCache.objects.get(
                    pk=parameterid)).save()
        self.logger.info("{} timeseries cached.".format(len(result.json)))
        return True
