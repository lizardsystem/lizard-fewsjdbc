# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_fewsjdbc.models import JdbcSource

from xmlrpclib import ResponseError


# L3
from lizard_map.views import WorkspaceView


class HomepageView(WorkspaceView):
    """
    Overview of all Jdbc Sources.
    """
    template_name = 'lizard_fewsjdbc/homepage.html'

    def get_context_data(self, **kwargs):
        # Take original context.
        context = super(HomepageView, self).get_context_data(**kwargs)

        # Add Breadcrumbs. TODO: make more generic.
        crumbs_prepend = kwargs.get('crumbs_prepend', None)
        if crumbs_prepend is not None:
            crumbs = list(crumbs_prepend)
        else:
            crumbs = [{'name': 'home', 'url': '/'}]
        crumbs.append({'name': 'metingen',
                       'title': 'metingen',
                       'url': reverse('lizard_fewsjdbc.homepage')})
        context['crumbs'] = crumbs

        # Add jdbc sources.
        context['jdbc_sources'] = JdbcSource.objects.all()

        return context


class JdbcSourceView(WorkspaceView):
    """
    FEWS JDBC browser view. Filter list and parameter list is cached.
    """
    template_name='lizard_fewsjdbc/jdbc_source.html'

    def get_context_data(self, **kwargs):
        # Take original context.
        context = super(JdbcSourceView, self).get_context_data(**kwargs)

        # Jdbc source slug: must be there
        jdbc_source_slug = kwargs['jdbc_source_slug']
        context['jdbc_source_slug'] = jdbc_source_slug

        filter_id = self.request.GET.get('filter_id', None)
        ignore_cache = self.request.GET.get('ignore_cache', False)
        jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)

        # Workspace_acceptables.
        # If the page is called with option filter_id, add parameter variables.
        workspace_acceptables = None
        fews_filter = None

        if filter_id is None:
            try:
                filter_tree = jdbc_source.get_filter_tree(
                    ignore_cache=ignore_cache)
            except ResponseError:
                # The JDBC source is probably down?
                filter_tree = [{'name': 'Fout bij het laden van filters.'}]
        else:
            filter_tree = None
            named_parameters = jdbc_source.get_named_parameters(
                filter_id, ignore_cache=ignore_cache)

            if named_parameters:
                workspace_acceptables = [
                    {'name': '%s (%s, %s)' % (
                            named_parameter['parameter'],
                            named_parameter['filter_name'],
                            jdbc_source_slug),
                     'shortname': '%s (%s)' % (
                            named_parameter['parameter'],
                            named_parameter['filter_name']),
                     #'name': '%s' % named_parameter['parameter'],
                     'id': named_parameter['parameterid'],
                     'filter_id': named_parameter['filter_id'],
                     'filter_name': named_parameter['filter_name'],
                     'adapter_class': 'adapter_fewsjdbc',
                     'adapter_layer_json': (
                            '{"slug": "%s", "filter": "%s", '
                            '"parameter": "%s"}') % (
                            jdbc_source_slug, named_parameter['filter_id'],
                            named_parameter['parameterid'])
                     }
                    for named_parameter in named_parameters]
                fews_filter = {'name': named_parameters[0]['filter_name'],
                               'id': filter_id}
        context['workspace_acceptables'] = workspace_acceptables
        context['fews_filter'] = fews_filter
        context['tree_items'] = filter_tree

        # Breadcrumbs.
        crumbs_prepend = kwargs.get('crumbs_prepend', None)
        if crumbs_prepend is not None:
            # Use list to prevent strange behaviour
            crumbs = list(crumbs_prepend)
        else:
            crumbs = [{'name': 'home', 'url': '/'}]
        crumbs.append({'name': jdbc_source.name,
                       'title': 'metingen %s' % jdbc_source.name,
                       'url': jdbc_source.get_absolute_url() +
                       '?ignore_cache=True' if ignore_cache else ''})
        context['crumbs'] = crumbs

        return context
