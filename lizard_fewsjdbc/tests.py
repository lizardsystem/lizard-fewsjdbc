# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

import datetime
import xmlrpclib

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from lizard_map.models import WorkspaceItemError

from lizard_fewsjdbc.models import JDBC_NONE
from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.models import IconStyle
from lizard_fewsjdbc.layers import FewsJdbc


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
        # self.mock_query_result['filter'] = [
        #     ['id1', 'name1', JDBC_NONE, 'filtername1'],
        #     ['id2', 'name2', 'id1', 'filtername2'],
        #     ['id3', 'name3', 'id1', 'filtername3'],
        #     ['id4', 'name4', 'id2', 'filtername4'],
        #     ]
        self.mock_query_result['parameter'] = [
            ['name1', 'parameterid1', 'parameter1', 'name1'],
            ['name2', 'parameterid2', 'parameter2', 'name2'],
            ['name3', 'parameterid3', 'parameter3', 'name3'],
            ]

        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'wro'})
        url += '?filter_id=Hoofd_waterstand_webserver&ignore_cache=True'
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
        url_base = '/fews_jdbc/assen/?filter_id=%s&ignore_cache=True'
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
            {'filter_name': 'name1', 'parameterid': 'parameterid1',
             'parameter': 'parameter1'},
            {'filter_name': 'name2', 'parameterid': 'parameterid2',
             'parameter': 'parameter2'},
            {'filter_name': 'name3', 'parameterid': 'parameterid3',
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


class TestIconStyle(TestCase):
    fixtures = ('lizard_fewsjdbc_test', )

    def test_styles(self):
        """See if styles() output correspond to database contents.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()

        expected = {
            '::::::':
            {'icon': 'icon.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)}}

        self.assertEqual(IconStyle._styles(), expected)

    def test_styles(self):
        """See if styles_lookup() output correspond to database contents.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='ff00ff').save()

        expected = {
            '::::::':
            {'icon': 'icon.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)},
            '::filter1::::':
            {'icon': 'filter1.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)}}

        self.assertEqual(IconStyle._styles(), expected)

    def test_lookup(self):
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png',
                  color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='par1',
                  icon='loc1par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='',
                  icon='loc1.png', mask='mask.png', color='00ffff').save()

        expected = {
            # Level0: jdbc_source_id
            None: {
                # Level1: fews_filter
                None: {
                    # Level2: fews_location
                    None: {
                        # Level3: fews_parameter
                        None: '::::::'
                       },
                    'loc1': {
                        # Level3: fews_parameter
                        None: '::::loc1::',
                        'par1': '::::loc1::par1'
                       }
                    },
                'filter1': {
                    # Level2: fews_location
                    None: {
                        # Level3: fews_parameter
                        None: '::filter1::::'
                       }
                    }
                }
            }

        self.assertEqual(IconStyle._lookup(), expected)

    def test_style(self):
        """See if style() output correspond to expected lookup.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='par1', fews_parameter='',
                  icon='par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='loc1',
                  fews_parameter='',
                  icon='loc1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='loc1',
                  fews_parameter='par1',
                  icon='par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='par1',
                  icon='loc1par1.png', mask='mask.png', color='00ffff').save()

        jdbc_source = JdbcSource.objects.all()[0]

        expected1 = (
            '::::::',
            {'icon': 'icon.png', 'mask': ('mask.png', ), 'color': (1.0, 0.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'locy', 'parz'),
            expected1)
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'locy', 'parz',
                            ignore_cache=True),
            expected1)

        expected2 = (
            '::filter1::::',
            {'icon': 'filter1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'l', 'p'),
            expected2)
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'l', 'p',
                            ignore_cache=True),
            expected2)

        expected3 = (
            '::filter1::loc1::',
            {'icon': 'loc1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'loc1', 'p'),
            expected3)

        expected4 = (
            '::filter1::loc1::par1',
            {'icon': 'par1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'loc1', 'par1'),
            expected4)

        expected5 = (
            '::::loc1::par1',
            {'icon': 'loc1par1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected5)

    def test_empty(self):
        """Do not crash when no iconstyles are available, just return default.
        """

        expected = (
            '::::::',
            {'icon': 'meetpuntPeil.png', 'mask': ('meetpuntPeil_mask.png', ),
             'color': (0.0, 0.5, 1.0, 1.0)})

        jdbc_source = JdbcSource.objects.all()[0]
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected)

    def test_not_found(self):
        """Do not crash when corresponding iconstyle is notavailable,
        just return default.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='00ffff').save()

        expected = (
            '::::::',
            {'icon': 'meetpuntPeil.png', 'mask': ('meetpuntPeil_mask.png', ),
             'color': (0.0, 0.5, 1.0, 1.0)})

        jdbc_source = JdbcSource.objects.all()[0]
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected)


class TestAdapter(TestCase):

    def test_bails_out(self):
        """If the jdbc source doesn't exist, raise a ws item error."""

        self.assertRaises(WorkspaceItemError,
                          FewsJdbc,
                          None,
                          layer_arguments={
                'slug': 'nonexisting',
                'filter': None,
                'parameter': None})
