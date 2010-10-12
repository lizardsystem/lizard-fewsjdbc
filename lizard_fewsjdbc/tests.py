# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase

from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.operations import tree_from_list


class TestModel(TestCase):

    def setUp(self):
        self.jdbc_source = JdbcSource(
            slug='wro',
            name='Waterschap Roer en Overmaas',
            jdbc_url='http://web.lizardsystem.nl:8090/Jdbc2Ei/test',
            jdbc_tag_name='url_wro_dev',
            connector_string='jdbc:vjdbc:rmi://127.0.0.1:2006/VJdbc,FewsDataStore')
        self.jdbc_source.save()

    def test_customfilter(self):
        """See if customfilters can be used"""
        self.jdbc_source.usecustomfilter = True
        self.jdbc_source.customfilter = (
            "[{'id':'id','name':'name','parentid':None}, "
            "{'id':'id2','name':'name2','parentid':'id'}]")
        self.jdbc_source.save()

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

    # def test_tree_from_list1(self):
    #     rows = []
    #     result_good = []
    #     result_function = tree_from_list(rows)
    #     self.assertEqual(result_function, result_good)

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
