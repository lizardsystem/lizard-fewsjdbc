"""Tests for lizard_fewsjdbc.models."""
from __future__ import unicode_literals

import factory

from django.test import TestCase
from lizard_fewsjdbc import models


class FilterCacheF(factory.Factory):
    FACTORY_FOR = models.FilterCache

    filterid = 'HHNK_Boezem_RUW'
    name = 'Oppervlaktewater'
    description = ''
    is_sub_filter = False
    parent_id = 'parent id'
    parent_name = 'parentname'
    is_end_node = False


class LocationCacheF(factory.Factory):
    FACTORY_FOR = models.LocationCache

    locationid = 'KNMI-RADAR'
    name = 'KNMI-RADAR'
    short_name = 'KNMI-RADAR'
    description = ''
    lng = float(3.3135831)
    lat = float(47.974766)
    tooltiptext = "<br>Test</br>"
    parent_id = None


class ParameterCacheF(factory.Factory):
    FACTORY_FOR = models.ParameterCache

    parameterid = 'windrichting.meting'
    name = 'windrichting gemeten'
    short_name = 'windrichting gemeten'
    unit = 'grade'
    parameter_type = 'instantaneous'
    parameter_group = 'wind'


class TimeseriesCacheF(factory.Factory):
    FACTORY_FOR = models.TimeseriesCache

    t_filter = factory.SubFactory(FilterCacheF)
    t_location = factory.SubFactory(LocationCacheF)
    t_parameter = factory.SubFactory(ParameterCacheF)


class TestFilterCache(TestCase):
    def test_has_unicode(self):
        filter_cache = FilterCacheF.build()
        uni = filter_cache.__unicode__()
        self.assertTrue(uni)
        self.assertTrue(isinstance(uni, unicode))


class TestLocationCache(TestCase):
    def test_has_unicode(self):
        location_cache = LocationCacheF.build()
        uni = location_cache.__unicode__()
        self.assertTrue(uni)
        self.assertTrue(isinstance(uni, unicode))


class TestParameterCache(TestCase):
    def test_has_unicode(self):
        parameter_cache = ParameterCacheF.build()
        uni = parameter_cache.__unicode__()
        self.assertTrue(uni)
        self.assertTrue(isinstance(uni, unicode))


class TestTimeseriesCache(TestCase):
    def test_has_unicode(self):
        timeseries_cache = TimeseriesCacheF.build()
        uni = timeseries_cache.__unicode__()
        self.assertTrue(uni)
        print uni + "============"
        print type(uni)
        self.assertTrue(isinstance(uni, unicode))
