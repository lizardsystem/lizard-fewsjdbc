# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

import datetime
import xmlrpclib

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from lizard_fewsjdbc.models import JDBC_NONE
from lizard_fewsjdbc.models import JdbcSource


class TestIntegration(TestCase):
    """
    Integration tests.

    This test uses a test client with actual connection data to
    connect to (should be) working and not working data sources.
    """
    fixtures = ['lizard_fewsjdbc_test']

    def mock_query(self, q):
        """
        Mock query function for JdbcSource. We have to see 'which' of
        the JdbcSource functions it is called from.
        """

        if 'timeseries' in q:
            # Timeseries: time, value, flag, detection, comment.
            return self.mock_query_result.get('timeseries', [])
        elif 'unit' in q:
            # Unit: unit.
            return self.mock_query_result.get('unit', [])
        elif 'where' in q:  # From here, the call is from filter_tree
                            # or parameters
            # Parameters: (filter) name, parameterid, parameter.
            return self.mock_query_result.get('parameter', [])
        else:
            # Filter_tree: id, name, parentid.
            return self.mock_query_result.get('filter', [])

    def setUp(self):
        self.query_orig = JdbcSource.query
        JdbcSource.query = self.mock_query
        self.mock_query_result = {}

    def tearDown(self):
        JdbcSource.query = self.query_orig

    def TestHomepage(self):
        """
        Homepage.
        """
        c = Client()
        url = reverse('lizard_fewsjdbc.homepage')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def TestWro(self):
        """
        Working jdbc source with custom filters.
        """
        self.mock_query_result['filter'] = [
            ['id1', 'name1', JDBC_NONE],
            ['id2', 'name2', 'id1'],
            ['id3', 'name3', 'id1'],
            ['id4', 'name4', 'id2'],
            ]

        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'wro'})
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def TestWroFilter(self):
        """
        Working jdbc source with custom filters.
        """
        self.mock_query_result['filter'] = [
            ['id1', 'name1', JDBC_NONE],
            ['id2', 'name2', 'id1'],
            ['id3', 'name3', 'id1'],
            ['id4', 'name4', 'id2'],
            ]
        self.mock_query_result['parameter'] = [
            ['name1', 'parameterid1', 'parameter1'],
            ['name2', 'parameterid2', 'parameter2'],
            ['name3', 'parameterid3', 'parameter3'],
            ]

        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'wro'})
        url += '?filter_id=Hoofd_waterstand_webserver'
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def TestAssen(self):
        """
        Working jdbc source.
        """
        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'wro'})
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def TestKapot(self):
        """
        The Jdbc2Ei is reachable, but the Jdbc itself returns an error.
        """
        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'kapot'})
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def TestKapot2(self):
        """
        Incorrect Jdbc2Ei url
        """
        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'kapot2'})
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class TestModelMockQuery(TestCase):
    fixtures = ['lizard_fewsjdbc']

    def mock_query(self, q):
        return self.mock_query_result

    def setUp(self):
        self.jdbc_source = JdbcSource.objects.get(slug='assen')
        self.query_orig = self.jdbc_source.query
        self.jdbc_source.query = self.mock_query
        self.mock_query_result = []

    def tearDown(self):
        self.jdbc_source.query = self.query_orig

    def test_get_filter_tree(self):
        """
        Get filter tree using mock query result
        """
        # Define mock result: id, name, parentid
        self.mock_query_result = [
            ['id1', 'name1', JDBC_NONE],
            ['id2', 'name2', 'id1'],
            ['id3', 'name3', 'id1'],
            ['id4', 'name4', 'id2'],
            ]
        result = self.jdbc_source.get_filter_tree(ignore_cache=True)
        url_base = '/fews_jdbc/assen/?filter_id=%s'
        result_good = [
            {'id': 'id1', 'name': 'name1',
             'url': url_base % 'id1',
             'parentid': JDBC_NONE, 'children': [
                    {'id': 'id2', 'name': 'name2',
                     'url': url_base % 'id2',
                     'parentid': 'id1', 'children': [
                            {'id': 'id4', 'name': 'name4',
                             'url': url_base % 'id4',
                             'parentid': 'id2', 'children': []},
                            ]},
                    {'id': 'id3', 'name': 'name3',
                     'url': url_base % 'id3',
                     'parentid': 'id1', 'children': []},
                    ]}
            ]
        self.assertEqual(result, result_good)

    def test_get_named_parameters(self):
        """
        Get parameter list using mock query result
        """
        # Define name, parameterid, parameter
        self.mock_query_result = [
            ['name1', 'parameterid1', 'parameter1'],
            ['name2', 'parameterid2', 'parameter2'],
            ['name3', 'parameterid3', 'parameter3'],
            ]
        result = self.jdbc_source.get_named_parameters('id1')
        result_good = [
            {'name': 'name1', 'parameterid': 'parameterid1',
             'parameter': 'parameter1'},
            {'name': 'name2', 'parameterid': 'parameterid2',
             'parameter': 'parameter2'},
            {'name': 'name3', 'parameterid': 'parameterid3',
             'parameter': 'parameter3'},
            ]
        self.assertEqual(result, result_good)

    def test_get_timeseries(self):
        class MockTime(object):
            def __init__(self, value):
                self.value = value

        class MockTzInfo(datetime.tzinfo):
            def utcoffset(self, dt):
                # Note: hardcoded to GMT+1.
                return datetime.timedelta(hours=1)
        # time, value, flag, detection, comment; time has a property
        # 'value'
        self.mock_query_result = [
            [MockTime('20100501T00:00:00'), '1.2', '0', '0', None],
            [MockTime('20100502T00:00:00'), '1.3', '0', '0', None],
            [MockTime('20100503T00:00:00'), '1.4', '0', '0', None],
            [MockTime('20100504T00:00:00'), '1.5', '0', '0', None],
            [MockTime('20100505T00:00:00'), '1.6', '0', '0', None],
            ]
        start_date = datetime.datetime(2010, 5, 1)
        end_date = datetime.datetime(2010, 6, 1)
        result = self.jdbc_source.get_timeseries(
            'id1', 'location1', 'parameter1', start_date, end_date)
        result_good = [
            {'time': datetime.datetime(2010, 5, 1, tzinfo=MockTzInfo()),
             'value': '1.2', 'flag': '0', 'detection': '0', 'comment': None},
            {'time': datetime.datetime(2010, 5, 2, tzinfo=MockTzInfo()),
             'value': '1.3', 'flag': '0', 'detection': '0', 'comment': None},
            {'time': datetime.datetime(2010, 5, 3, tzinfo=MockTzInfo()),
             'value': '1.4', 'flag': '0', 'detection': '0', 'comment': None},
            {'time': datetime.datetime(2010, 5, 4, tzinfo=MockTzInfo()),
             'value': '1.5', 'flag': '0', 'detection': '0', 'comment': None},
            {'time': datetime.datetime(2010, 5, 5, tzinfo=MockTzInfo()),
             'value': '1.6', 'flag': '0', 'detection': '0', 'comment': None},
            ]
        self.assertEqual(result, result_good)

    def test_get_unit(self):
        self.mock_query_result = [
            ['mock_unit'],
            ]
        result = self.jdbc_source.get_unit('parameter')
        result_good = 'mock_unit'
        self.assertEqual(result, result_good)


class TestModel(TestCase):
    fixtures = ['lizard_fewsjdbc']

    class MockServerProxy(object):

        def __init__(self, url):
            pass

        class Ping(object):
            @classmethod
            def isAlive(self, a, b):
                return 0

        class Config(object):
            @classmethod
            def get(self, a, b, name):
                return 'http://...'

            @classmethod
            def put(self, a, b, name, value):
                return 0

        class Query(object):
            @classmethod
            def execute(self, a, b, query, l):
                if not isinstance(l, list):
                    raise ("Query.execute expected a list as "
                           "4th parameter. Instead: %r" % l)
                return [["mock result"]]

    def test_customfilter(self):
        """See if customfilters can be used"""
        jdbc_source = JdbcSource.objects.get(slug='assen')
        jdbc_source.usecustomfilter = True
        jdbc_source.customfilter = (
            "[{'id':'id','name':'name','parentid':None}, "
            "{'id':'id2','name':'name2','parentid':'id'}]")
        jdbc_source.save()

    def test_customfilter2(self):
        """See if filtertree can be retrieved."""
        jdbc_source = JdbcSource.objects.get(slug='wro')
        jdbc_source.get_filter_tree()

    def test_query(self):
        """
        Set up some mock server proxy, then run the function
        """
        server_proxy_orig = xmlrpclib.ServerProxy
        xmlrpclib.ServerProxy = self.MockServerProxy

        jdbc_source = JdbcSource.objects.get(slug='wro')

        result = jdbc_source.query('select * from filters;')
        result_good = [["mock result"]]

        xmlrpclib.ServerProxy = server_proxy_orig

        self.assertEqual(result, result_good)

    # def test_customfilter_invalid(self):
    #     """See if invalid customfilters can be saved"""
    #     self.jdbc_source.usecustomfilter = True
    #     self.jdbc_source.customfilter = (
    #         "[{'id':'id','namtid':None}, "
    #         "{'id':e':'name2','parentid':'id'}]")
    #     self.jdbc_source.save()


class TestAdapter(TestCase):

    def test_dummy(self):
        pass
