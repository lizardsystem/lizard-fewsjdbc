# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_fewsjdbc.models import JDBC_NONE
from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.operations import named_list
from lizard_fewsjdbc.operations import tree_from_list
from lizard_fewsjdbc.operations import unique_list
from lizard_map.daterange import current_start_end_dates
from lizard_map.daterange import DateRangeForm
from lizard_map.workspace import WorkspaceManager

FILTER_CACHE_KEY = 'lizard_fewsjdbc.views.filter_cache_key'


def homepage(request,
             javascript_click_handler='popup_click_handler',
             javascript_hover_handler='popup_hover_handler',
             template="lizard_fewsjdbc/homepage.html"):
    """
    Overview of all Jdbc Sources.
    """

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()
    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))

    return render_to_response(
        template,
        {'javascript_hover_handler': javascript_hover_handler,
         'javascript_click_handler': javascript_click_handler,
         'date_range_form': date_range_form,
         'jdbc_sources': JdbcSource.objects.all(),
         'workspaces': workspaces},
        context_instance=RequestContext(request))


def jdbc_source(request,
                jdbc_source_slug,
                javascript_click_handler='popup_click_handler',
                javascript_hover_handler='popup_hover_handler',
                template="lizard_fewsjdbc/jdbc_source.html"):
    """
    FEWS JDBC browser view. Filter list and parameter list is cached.
    """

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()
    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))
    filter_id = request.GET.get('filter_id', None)
    jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)

    filter_source_cache_key = FILTER_CACHE_KEY + '::' + jdbc_source_slug
    filter_tree = cache.get(filter_source_cache_key)
    if filter_tree is None:
        # Building up the fews filter tree.
        filters = jdbc_source.query("select id, name, parentid from filters;")
        unique_filters = unique_list(filters)
        named_filters = named_list(unique_filters, ['id', 'name', 'parentid'])
        # Add url per filter.
        for named_filter in named_filters:
            url = reverse('lizard_fewsjdbc.jdbc_source',
                          kwargs={'jdbc_source_slug': jdbc_source_slug})
            url += '?filter_id=%s' % named_filter['id']
            named_filter['url'] = url
        # Make the tree.
        filter_tree = tree_from_list(
            named_filters,
            id_field='id',
            parent_field='parentid',
            children_field='children',
            root_parent=JDBC_NONE)
        cache.set(filter_source_cache_key, filter_tree, 8 * 60 * 60)

    # If the page is called with option filter_id, add parameter variables.
    fews_parameters = None
    fews_filter = None

    if filter_id is not None:
        parameter_cache_key = filter_source_cache_key + '::' + str(filter_id)
        named_parameters = cache.get(parameter_cache_key)

        if named_parameters is None:
            parameter_result = jdbc_source.query(
                ("select name, parameterid, parameter "
                 "from filters where id='%s'" % filter_id))
            unique_parameters = unique_list(parameter_result)
            named_parameters = named_list(unique_parameters,
                                          ['name', 'parameterid', 'parameter'])
            cache.set(parameter_cache_key, named_parameters, 8 * 60 * 60)

        if named_parameters:
            for named_parameter in named_parameters:
                fews_parameters = [{'name': named_parameter['parameter'],
                                    'id': named_parameter['parameterid']}]
            fews_filter = {'name': named_parameters[0]['name'],
                           'id': filter_id}

    return render_to_response(
        template,
        {'javascript_hover_handler': javascript_hover_handler,
         'javascript_click_handler': javascript_click_handler,
         'date_range_form': date_range_form,
         'tree_items': filter_tree,
         'parameters': fews_parameters,
         'filter': fews_filter,
         'jdbc_source_slug': jdbc_source_slug,
         'workspaces': workspaces},
        context_instance=RequestContext(request))
