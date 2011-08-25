# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_fewsjdbc.models import JdbcSource


def homepage(request,
             template="lizard_fewsjdbc/homepage.html",
             crumbs_prepend=None):
    """
    Overview of all Jdbc Sources.
    """

    if crumbs_prepend is not None:
        crumbs = list(crumbs_prepend)
    else:
        crumbs = [{'name': 'home', 'url': '/'}]
    crumbs.append({'name': 'metingen',
                   'title': 'metingen',
                   'url': reverse('lizard_fewsjdbc.homepage')})

    return render_to_response(
        template,
        {'jdbc_sources': JdbcSource.objects.all(),
         'crumbs': crumbs},
        context_instance=RequestContext(request))


def jdbc_source(request,
                jdbc_source_slug,
                template="lizard_fewsjdbc/jdbc_source.html",
                adapter_class="adapter_fewsjdbc",
                crumbs_prepend=None):
    """
    FEWS JDBC browser view. Filter list and parameter list is cached.
    """

    filter_id = request.GET.get('filter_id', None)
    ignore_cache = request.GET.get('ignore_cache', False)
    jdbc_source = JdbcSource.objects.get(slug=jdbc_source_slug)

    # If the page is called with option filter_id, add parameter variables.
    fews_parameters = None
    fews_filter = None

    if filter_id is None:
        filter_tree = jdbc_source.get_filter_tree(ignore_cache=ignore_cache)
    else:
        filter_tree = None
        named_parameters = jdbc_source.get_named_parameters(
            filter_id, ignore_cache=ignore_cache)

        if named_parameters:
            fews_parameters = [
                {'name': '%s' % named_parameter['parameter'],
                 'id': named_parameter['parameterid'],
                 'filter_id': named_parameter['filter_id'],
                 'filter_name': named_parameter['filter_name']}
                for named_parameter in named_parameters]
            fews_filter = {'name': named_parameters[0]['filter_name'],
                           'id': filter_id}

    if crumbs_prepend is not None:
        crumbs = list(crumbs_prepend)  # Use list to prevent strange behaviour
    else:
        crumbs = [{'name': 'home', 'url': '/'}]
    crumbs.append({'name': jdbc_source.name,
                   'title': 'metingen %s' % jdbc_source.name,
                   'url': jdbc_source.get_absolute_url() +
                          '?ignore_cache=True' if ignore_cache else ''})

    return render_to_response(
        template,
        {'tree_items': filter_tree,
         'parameters': fews_parameters,
         'filter': fews_filter,
         'jdbc_source_slug': jdbc_source_slug,
         'adapter_class': adapter_class,
         'crumbs': crumbs},
        context_instance=RequestContext(request))
