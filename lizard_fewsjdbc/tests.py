# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from lizard_fewsjdbc.models import JDBC_NONE
from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.operations import AnchestorRegistration
from lizard_fewsjdbc.operations import CycleError
from lizard_fewsjdbc.operations import named_list
from lizard_fewsjdbc.operations import tree_from_list
from lizard_fewsjdbc.operations import unique_list


class TestIntegration(TestCase):
    """
    Integration tests.

    This test uses a test client with actual connection data to
    connect to (should be) working and not working data sources.
    """
    fixtures = ['lizard_fewsjdbc_test']

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
        c = Client()
        url = reverse('lizard_fewsjdbc.jdbc_source',
                      kwargs={'jdbc_source_slug': 'wro'})
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
        result = self.jdbc_source.get_filter_tree()
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

    # def test_get_timeseries(self):
    #     self.mock_query_result = []
    #     result = self.jdbc_source.get_timeseries(
    #         'id1', 'location1', 'parameter1', start_date, end_date)

    def test_get_unit(self):
        pass


class TestModel(TestCase):
    fixtures = ['lizard_fewsjdbc']

    def test_customfilter(self):
        """See if customfilters can be used"""
        self.jdbc_source = JdbcSource.objects.get(slug='assen')
        self.jdbc_source.usecustomfilter = True
        self.jdbc_source.customfilter = (
            "[{'id':'id','name':'name','parentid':None}, "
            "{'id':'id2','name':'name2','parentid':'id'}]")
        self.jdbc_source.save()

    def test_customfilter2(self):
        """See if filtertree can be retrieved."""
        jdbc_source = JdbcSource.objects.get(slug='wro')
        jdbc_source.get_filter_tree()

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


class TestOperations(TestCase):

    def test_anchestor_registration(self):
        """Check basic functionality"""
        anchestors = AnchestorRegistration()
        self.assertFalse(anchestors.anchestor_of('child', 'parent'))
        anchestors.register_parent('child', 'parent')
        self.assertTrue(anchestors.anchestor_of('child', 'parent'))
        anchestors.register_parent('grandchild', 'child')
        self.assertTrue(anchestors.anchestor_of('grandchild', 'parent'))
        self.assertFalse(anchestors.anchestor_of('parent', 'grandchild'))

    def test_anchestor_registration2(self):
        """The anchestor registration doesn't mind cycles"""
        anchestors = AnchestorRegistration()
        anchestors.register_parent('child', 'parent')
        anchestors.register_parent('parent', 'child')
        self.assertTrue(anchestors.anchestor_of('child', 'parent'))
        self.assertTrue(anchestors.anchestor_of('parent', 'child'))

    def test_tree_from_list1(self):
        rows = []
        result_good = []
        result_function = tree_from_list(rows)
        self.assertEqual(result_function, result_good)

    def test_tree_from_list2(self):
        rows = [{'name': 'parent_name', 'parent': None},
                {'name': 'child_name', 'parent': 'parent_name'}]
        result_good = [
                {'name': 'parent_name',
                 'parent': None,
                 'children': [
                    {'name': 'child_name',
                     'parent': 'parent_name',
                     'children': []}]}]
        result_function = tree_from_list(
            rows,
            id_field='name',
            parent_field='parent',
            children_field='children',
            root_parent=None)
        self.assertEqual(result_function, result_good)

    def test_tree_from_list3(self):
        rows = [{'name': 'parent_name', 'parent': None},
                {'name': 'child_name', 'parent': 'parent_name'},
                {'name': 'child_name2', 'parent': 'parent_name'},
                {'name': 'child_name3', 'parent': 'parent_name'},
                {'name': 'child_child', 'parent': 'child_name3'}]
        result_good = [
                {'name': 'parent_name',
                 'parent': None,
                 'children': [
                    {'name': 'child_name',
                     'parent': 'parent_name',
                     'children': []},
                    {'name': 'child_name2',
                     'parent': 'parent_name',
                     'children': []},
                    {'name': 'child_name3',
                     'parent': 'parent_name',
                     'children': [
                         {'name': 'child_child',
                          'parent': 'child_name3',
                          'children': []}]},
                     ]}]
        result_function = tree_from_list(
            rows,
            id_field='name',
            parent_field='parent',
            children_field='children',
            root_parent=None)
        self.assertEqual(result_function, result_good)

    def test_tree_from_list_cyclic(self):
        """
        Cycle detection 1
        """
        rows = [{'name': 'child_name', 'parent': 'parent_name'},
                {'name': 'parent_name', 'parent': 'child_name'}]
        self.assertRaises(
            CycleError,
            tree_from_list,
            rows,
            id_field='name',
            parent_field='parent',
            children_field='children',
            root_parent='parent_name')

    def test_tree_from_list_cyclic2(self):
        """
        Cycle detection 2
        """
        rows = [{'name': 'parent_name', 'parent': 'parent_name'}, ]
        self.assertRaises(
            CycleError,
            tree_from_list,
            rows,
            id_field='name',
            parent_field='parent',
            children_field='children',
            root_parent='child_name')

    def test_named_list(self):
        rows = [
            ['a', 'b', 'c', 'd'],
            ['f', 'g', 'h', 'i']]
        names = ['name1', 'name2', 'name3', 'name4']
        result = named_list(rows, names)
        result_good = [
            {'name1': 'a', 'name2': 'b', 'name3': 'c', 'name4': 'd'},
            {'name1': 'f', 'name2': 'g', 'name3': 'h', 'name4': 'i'}]
        self.assertEqual(result, result_good)

    def test_unique_list(self):
        rows = [1, 2, 2, 3, 4, 5, 5, 7, 2, 5]
        result = unique_list(rows)
        result_good = [1, 2, 3, 4, 5, 7]
        self.assertEqual(result, result_good)

    def test_unique_list2(self):
        rows = [[1, 2], [2, 2], [3, 4], [2, 2], [1, 2]]
        result = unique_list(rows)
        result_good = [[1, 2], [2, 2], [3, 4]]
        self.assertEqual(result, result_good)
