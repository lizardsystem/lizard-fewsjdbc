# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from lizard_fewsjdbc.models import JdbcSource
from lizard_map.views import AppView


class HomepageView(AppView):
    """Class based view for the fewsjdbc homepage.

    TODO: crumbs don't work yet."""

    template_name = 'lizard_fewsjdbc/homepage.html'

    def jdbc_sources(self):
        return JdbcSource.objects.all()

    def crumbs(self):
        """TODO: This doesn't actually do anything yet.

        The crumbs are rendered in lizard_ui and at the present moment
        that doesn't expect a class based view."""
        return [{'name': 'home', 'url': '/'},
                {'name': 'metingen',
                  'title': 'metingen',
                  'url': reverse('lizard_fewsjdbc.homepage')}]


class JdbcSourceView(AppView):
    """Class based view for the fewsjdbc filters/parameters blocks
    contained in a given jdbc source."""

    template_name = "lizard_fewsjdbc/jdbc_source.html"
    filter_url_name = "lizard_fewsjdbc.jdbc_source"
    adapter_class = "adapter_fewsjdbc"

    def get(self, request, *args, **kwargs):
        """This method is overridden in order to get at the GET parameters."""

        self.jdbc_source_slug = kwargs.get('jdbc_source_slug', '')
        self.jdbc_source = get_object_or_404(JdbcSource,
                                             slug=self.jdbc_source_slug)
        self.filter_id = request.GET.get('filter_id', None)
        self.ignore_cache = request.GET.get('ignore_cache', False)

        return super(JdbcSourceView, self).get(request, *args, **kwargs)

    def tree_items(self):
        """If there is no filter chosen yet, show the filter tree."""
        if self.filter_id is None:
            return self.jdbc_source.get_filter_tree(
                self.filter_url_name,
                ignore_cache=self.ignore_cache)
        else:
            return None

    def parameters(self):
        """If there is a filter chosen, show its parameters."""
        if self.filter_id is not None:
            named_parameters = self.jdbc_source.get_named_parameters(
                self.filter_id, ignore_cache=self.ignore_cache)

            if named_parameters:
                return [
                    {'name': '%s' % named_parameter['parameter'],
                     'workspace_name': ('%s (%s, %s)' %
                                        (named_parameter['parameter'],
                                        named_parameter['filter_name'],
                                        self.jdbc_source_slug)),
                     'id': named_parameter['parameterid'],
                     'filter_id': named_parameter['filter_id'],
                     'filter_name': named_parameter['filter_name']}
                    for named_parameter in named_parameters]

    def filter(self):
        """Return the current filter."""
        if self.filter_id is not None:
            named_parameters = self.jdbc_source.get_named_parameters(
                self.filter_id, ignore_cache=self.ignore_cache)

            if named_parameters:
                return {'name': named_parameters[0]['filter_name'],
                        'id': self.filter_id}
