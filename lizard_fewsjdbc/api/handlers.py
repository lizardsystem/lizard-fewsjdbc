# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
"""
Handlers for the REST api provided through django-piston.


"""
import pkg_resources
from django.core.urlresolvers import reverse
from piston.handler import BaseHandler
from piston.doc import generate_doc

from lizard_map.api.handlers import documentation

from lizard_fewsjdbc.models import JdbcSource

FILTER_URL_NAME = 'api_jdbc_filters'
PARAMETER_URL_NAME = 'api_jdbc_parameters'


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
            data.append({'name': jdbc_source.name,
                         'url': url})
        result['data'] = data
        return result


class FilterHandler(BaseHandler):
    """Show available filters for a FEWS jdbc.

    The returned structure is nested as filters are hierarchical.
    Folders have a ``name`` and a ``children`` key, end nodes with
    data have ``name`` and ``url``.  The URL points at the available
    parameters for that filter.

    """
    allowed_methods = ('GET',)

    def _return_data(self, tree, request, jdbc_source_slug):
        """Return tree filtered to what we need."""
        result = []
        for item in tree:
            node = {}
            node['name'] = item['name']
            if not 'children' in item:
                # Some jdbc connection error.
                result= [node]
                return result
            if item['children']:
                # We're a folder.
                node['children'] = self._return_data(
                    item['children'], request, jdbc_source_slug)
            else:
                # We're an end node.
                url = request.build_absolute_uri(
                    reverse(
                        PARAMETER_URL_NAME,
                        kwargs={'jdbc_source_slug': jdbc_source_slug,
                                'filter_id': item['id']}))
                node['url'] = url
            result.append(node)
        return result

    def read(self, request, jdbc_source_slug):
        result = {}
        result['info'] = documentation(self.__class__)
        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)
        data = []
        result['data'] = self._return_data(
            jdbc_source.get_filter_tree(),
            request, jdbc_source_slug)
        return result


class ParameterHandler(BaseHandler):
    # TODO
    pass
