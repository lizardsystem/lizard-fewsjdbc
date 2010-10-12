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

    filters = [{'name': 'filter 1', 'children': None},
               {'name': 'filter 2', 'children': [
                {'name': 'filter 2a', 'children': None},
                {'name': 'filter 2b', 'children': None},
                ]},
               ]

    return render_to_response(
        template,
        {'javascript_hover_handler': javascript_hover_handler,
         'javascript_click_handler': javascript_click_handler,
         'date_range_form': date_range_form,
         'filters': filters,
         'workspaces': workspaces},
        context_instance=RequestContext(request))
