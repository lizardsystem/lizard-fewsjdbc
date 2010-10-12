# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_fewsjdbc.models import JdbcSource
from lizard_map.daterange import current_start_end_dates
from lizard_map.daterange import DateRangeForm
from lizard_map.workspace import WorkspaceManager


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
    FEWS JDBC browser view.
    """

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()
    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))

    filter_tree = [
        {'name': 'filter 1', 'url': 'http://amplivibe.com', 'children': None},
        {'name': 'filter 2', 'url': '', 'children': [
                {'name': 'filter 2a', 'url': '', 'children': None},
                {'name': 'filter 2b', 'url': '', 'children': None},
                ]},
        ]
    fews_parameters = None
    fews_filter = None

    return render_to_response(
        template,
        {'javascript_hover_handler': javascript_hover_handler,
         'javascript_click_handler': javascript_click_handler,
         'date_range_form': date_range_form,
         'filter_tree': filter_tree,
         'tree_items': filter_tree,
         'parameters': fews_parameters,
         'filter': fews_filter,
         'workspaces': workspaces},
        context_instance=RequestContext(request))
