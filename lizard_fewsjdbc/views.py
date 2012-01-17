# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from lizard_fewsjdbc.models import JdbcSource
from lizard_map.views import AppView

import logging
logger = logging.getLogger(__name__)

class HomepageView(AppView):
    """Class based view for the fewsjdbc homepage."""

    template_name = 'lizard_fewsjdbc/homepage.html'

    def jdbc_sources(self):
        return JdbcSource.objects.all()


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
        if not hasattr(self, '_parameters') and self.filter_id is not None:
            named_parameters = self.jdbc_source.get_named_parameters(
                self.filter_id, ignore_cache=self.ignore_cache)

            if named_parameters:
                self._parameters = [
                    {'name': '%s' % named_parameter['parameter'],
                     'workspace_name': ('%s (%s, %s)' %
                                        (named_parameter['parameter'],
                                        named_parameter['filter_name'],
                                        self.jdbc_source_slug)),
                     'id': named_parameter['parameterid'],
                     'filter_id': named_parameter['filter_id'],
                     'filter_name': named_parameter['filter_name']}
                    for named_parameter in named_parameters]
        if hasattr(self, '_parameters'):
            return self._parameters

    def filter(self):
        """Return the current filter."""
        if not hasattr(self, '_filter') and self.filter_id is not None:
            named_parameters = self.jdbc_source.get_named_parameters(
                self.filter_id, ignore_cache=self.ignore_cache)

            if named_parameters:
                self._filter = {'name': named_parameters[0]['filter_name'],
                        'id': self.filter_id}
        if hasattr(self, '_filter'):
            return self._filter

    def crumbs(self):
        crumbs = super(JdbcSourceView, self).crumbs()

        if self.jdbc_source_slug:
            # Sometimes people link from the app screens directly to some
            # JDBC source. In that case, it shouldn't be part of the breadcrumbs.
            # If they don't, people first saw the HomepageView and chose a 
            # source there, in that case we should show it.
            #
            # We can tell the difference because our super() search for an app
            # screen that was used to get to this point. If the source slug
            # is part of self.url_after_app, then the source slug wasn't used in
            # the app's url.

            if self.jdbc_source_slug in self.url_after_app:
                crumbs += [{
                    'url': reverse('lizard_fewsjdbc.jdbc_source',
                                   kwargs={'jdbc_source_slug': self.jdbc_source_slug}),
                    'description': self.jdbc_source.name,
                    'title': self.jdbc_source.name}]

            # If there is a filter selected, we can add it to the URL too
            f = self.filter()
            if f:
                crumbs += [{
                        'url': ('%s?filter_id=%s' % (reverse('lizard_fewsjdbc.jdbc_source',
                                                             kwargs={'jdbc_source_slug': self.jdbc_source_slug}),
                                                     f['id'])),
                        'description': f['name'],
                        'title': f['name']}]

        return crumbs
