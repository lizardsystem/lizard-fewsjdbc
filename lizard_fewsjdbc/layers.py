import datetime
import logging
import mapnik
import math
import os

from django.conf import settings
from django.http import Http404
from lizard_map import coordinates
from lizard_map import workspace
from lizard_map.adapter import Graph
from lizard_map.mapnik_helper import add_datasource_point
from lizard_map.models import ICON_ORIGINALS
from lizard_map.models import WorkspaceItemError
from lizard_map.symbol_manager import SymbolManager

from lizard_fewsjdbc.models import IconStyle
from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.models import FewsJdbcQueryError

logger = logging.getLogger('lizard_fewsunblobbed.layers')

JDBC_API_URL_NAME = 'api_jdbcs'
LAYER_STYLES = {
    "default": {'icon': 'meetpuntPeil.png',
                'mask': ('meetpuntPeil_mask.png', ),
                'color': (0, 0, 1, 0)},
    "Waterkwaliteit_REST": {'icon': 'meetpuntPeil.png',
                            'mask': ('meetpuntPeil_mask.png', ),
                            'color': (1, 1, 0, 0)},
    }

EPSILON = 0.0001


def fews_symbol_name(
    jdbc_source, filterkey, locationkey, parameterkey, nodata=False,
    styles=None, lookup=None):
    """
    Find fews symbol name.
    Copied from lizard_fewsunblobbed.
    """

    # determine icon layout by looking at filter.id
    # style_name = 'adf'
    # if str(filterkey) in LAYER_STYLES:
    #     icon_style = copy.deepcopy(LAYER_STYLES[str(filterkey)])
    # else:
    #     icon_style = copy.deepcopy(LAYER_STYLES['default'])

    style_name, icon_style = IconStyle.style(
        jdbc_source, filterkey, locationkey, parameterkey, styles, lookup)

    #make icon grey
    if nodata:
        icon_style['color'] = (0.9, 0.9, 0.9, 0)

    # apply icon layout using symbol manager
    symbol_manager = SymbolManager(
        ICON_ORIGINALS,
        os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
    output_filename = symbol_manager.get_symbol_transformed(
        icon_style['icon'], **icon_style)

    return style_name, output_filename


def fews_point_style(
    jdbc_source, filterkey, locationkey, parameterkey, nodata=False,
    styles=None, lookup=None):
    """
    Make mapnik point_style for fews point with given filterkey.
    Copied from lizard_fewsunblobbed.
    """
    point_style_name, output_filename = fews_symbol_name(
        jdbc_source, filterkey, locationkey, parameterkey,
        nodata, styles, lookup)
    output_filename_abs = os.path.join(
        settings.MEDIA_ROOT, 'generated_icons', output_filename)

    # use filename in mapnik pointsymbolizer
    point_looks = mapnik.PointSymbolizer(
        str(output_filename_abs), 'png', 16, 16)
    point_looks.allow_overlap = True
    layout_rule = mapnik.Rule()
    layout_rule.symbols.append(point_looks)

    # We use 'class' to filter the correct style for the locations
    layout_rule.filter = mapnik.Filter(
        "[style] = '%s'" % str(point_style_name))

    point_style = mapnik.Style()
    point_style.rules.append(layout_rule)

    return point_style_name, point_style


class FewsJdbc(workspace.WorkspaceItemAdapter):
    """
    Registered as adapter_fewsjdbc.
    """

    plugin_api_url_name = JDBC_API_URL_NAME

    def __init__(self, *args, **kwargs):
        super(FewsJdbc, self).__init__(
            *args, **kwargs)
        self.jdbc_source_slug = self.layer_arguments['slug']
        self.filterkey = self.layer_arguments['filter']
        self.parameterkey = self.layer_arguments['parameter']
        try:
            self.jdbc_source = JdbcSource.objects.get(
                slug=self.jdbc_source_slug)
        except JdbcSource.DoesNotExist:
            raise WorkspaceItemError(
                "Jdbc source %s doesn't exist." % self.jdbc_source_slug)

    def _locations(self):
        return self.jdbc_source.get_locations(self.filterkey,
                                              self.parameterkey)

    def layer(self, layer_ids=None, webcolor=None, request=None):
        """Return layer and styles that render points.

        """
        layers = []
        styles = {}
        layer = mapnik.Layer("FEWS JDBC points layer", coordinates.WGS84)

        layer.datasource = mapnik.PointDatasource()

        try:
            named_locations = self._locations()
        except FewsJdbcQueryError:
            logger.exception('Problem querying locations from jdbc2ei.')
            return [], {}

        fews_styles, fews_style_lookup = IconStyle._styles_lookup()

        logger.debug("Number of point objects: %d" % len(named_locations))
        for named_location in named_locations:
            logger.debug('layer coordinates %s %s %s' % (
                    named_location['locationid'],
                    named_location['longitude'],
                    named_location['latitude']))

            point_style_name, point_style = fews_point_style(
                self.jdbc_source,
                self.filterkey,
                named_location['locationid'],
                self.parameterkey,
                nodata=False,
                styles=fews_styles,
                lookup=fews_style_lookup)

            # Put style in point, filters work on these styles.
            add_datasource_point(
                layer.datasource, named_location['longitude'],
                named_location['latitude'], 'style', str(point_style_name))

            # generate "unique" point style name and append to layer
            # if the same style occurs multiple times, it will overwrite old.
            style_name = str("Lizard-FewsJdbc::%s" % (point_style_name))
            styles[style_name] = point_style

        # Add all style names to the layer styles.
        for style_name in styles.keys():
            layer.styles.append(style_name)

        layers = [layer, ]
        return layers, styles

    def extent(self, identifiers=None):
        """
        TODO: filter on identifiers.
        """
        logger.debug("Started calculating extent")
        north = None
        south = None
        east = None
        west = None
        named_locations = self._locations()
        wgs0coord_x, wgs0coord_y = coordinates.rd_to_wgs84(0.0, 0.0)

        for named_location in named_locations:
            x = named_location['longitude']
            y = named_location['latitude']
            # Ignore rd coordinates (0, 0).
            if (abs(x - wgs0coord_x) > EPSILON or
                abs(y - wgs0coord_y) > EPSILON):

                if x > east or east is None:
                    east = x
                if x < west or west is None:
                    west = x
                if y < south or south is None:
                    south = y
                if y > north or north is None:
                    north = y
            else:
                logger.warn("Location (%s, %s) at RD coordinates 0,0" %
                            (named_location['location'],
                             named_location['locationid']))
        west_transformed, north_transformed = coordinates.wgs84_to_google(
            west, north)
        east_transformed, south_transformed = coordinates.wgs84_to_google(
            east, south)
        logger.debug("Finished calculating extent")

        return {
            'north': north_transformed,
            'west': west_transformed,
            'south': south_transformed,
            'east': east_transformed}

    def search(self, google_x, google_y, radius=None):
        """Return list of dict {'distance': <float>, 'timeserie':
        <timeserie>} of closest fews point that matches x, y, radius.

        """
        def distance(x1, y1, x2, y2):
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        named_locations = self._locations()

        result = []
        for named_location in named_locations:
            x, y = coordinates.wgs84_to_google(
                named_location['longitude'],
                named_location['latitude'])
            dist = distance(google_x, google_y, x, y)
            if dist < radius:
                result.append(
                    {'distance': dist,
                     'name': named_location['location'],
                     'shortname': named_location['location'],
                     'workspace_item': self.workspace_item,
                     'identifier': {'location': named_location['locationid']},
                     'google_coords': (x, y),
                     'object': None})
        result.sort(key=lambda item: item['distance'])
        return result[:3]  # Max 3.

    def values(self, identifier, start_date, end_date):
        timeseries = self.jdbc_source.get_timeseries(
            self.filterkey, identifier['location'], self.parameterkey,
            start_date, end_date)
        unit = self.jdbc_source.get_unit(self.parameterkey)
        result = []
        for row in timeseries:
            result.append({'value': row['value'],
                           'datetime': row['time'],
                           'unit': unit})
        return result

    def value_aggregate(self, identifier, aggregate_functions,
                        start_date, end_date):
        return super(
            FewsJdbc,
            self).value_aggregate_default(
            identifier, aggregate_functions, start_date, end_date)

    def location(self, location, layout=None):
        # TODO: do the list -> dict conversion only once
        dict_locations = {}
        for named_location in self._locations():
            dict_locations[named_location['locationid']] = named_location
        location_name = dict_locations[location]['location']
        identifier = {'location': location}
        if layout is not None:
            identifier['layout'] = layout

        x, y = coordinates.wgs84_to_google(
            dict_locations[location]['longitude'],
            dict_locations[location]['latitude'])

        return {
            'name': location_name,
            'shortname': dict_locations[location]['location'],
            'workspace_item': self.workspace_item,
            'identifier': identifier,
            'google_coords': (x, y),
            'object': None}

    def image(self,
              identifiers,
              start_date,
              end_date,
              width=380.0,
              height=250.0,
              layout_extra=None,
              raise_404_if_empty=False):

        """
        Visualize timeseries in a graph.

        Legend is always drawn.

        TODO: option x-label does not work. Graph is too high?
        TODO: y_min, y_max does not work.
        """

        def apply_layout(layout, title, y_min, y_max, legend):
            """Applies layout options. Returns title,
            y_min, y_max, graph, legend

            From lizard-fewsunblobbed"""

            if "title" in layout:
                title = layout['title']
            if "y_min" in layout:
                y_min = float(layout['y_min'])
            if "y_max" in layout:
                y_max = float(layout['y_max'])
            if "legend" in layout:
                legend = layout['legend']
            if "y_label" in layout:
                graph.axes.set_ylabel(layout['y_label'])
            if "x_label" in layout:
                graph.set_xlabel(layout['x_label'])
            return title, y_min, y_max, legend

        def apply_lines(identifier, values, location_name):
            """Adds lines that are defined in layout. Uses function
            variable graph, line_styles.

            Inspired by fewsunblobbed"""

            layout = identifier['layout']

            if "line_min" in layout:
                graph.axes.axhline(
                    min(values),
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['min_linewidth'],
                    ls=line_styles[str(identifier)]['min_linestyle'],
                    label='Minimum %s' % location_name)
            if "line_max" in layout:
                graph.axes.axhline(
                    max(values),
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['max_linewidth'],
                    ls=line_styles[str(identifier)]['max_linestyle'],
                    label='Maximum %s' % location_name)
            if "line_avg" in layout and values:
                average = sum(values) / len(values)
                graph.axes.axhline(
                    average,
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['avg_linewidth'],
                    ls=line_styles[str(identifier)]['avg_linestyle'],
                    label='Gemiddelde %s' % location_name)

        line_styles = self.line_styles(identifiers)
        named_locations = self._locations()
        today = datetime.datetime.now()
        graph = Graph(start_date, end_date,
                      width=width, height=height, today=today)
        graph.axes.grid(True)
        unit = self.jdbc_source.get_unit(self.parameterkey)
        graph.axes.set_ylabel(unit)

        # Draw extra's (from fewsunblobbed)
        title = None
        y_min, y_max = None, None
        legend = None

        is_empty = True
        for identifier in identifiers:
            filter_id = self.filterkey
            location_id = identifier['location']
            location_name = [
                location['location'] for location in named_locations
                if location['locationid'] == location_id][0]

            parameter_id = self.parameterkey
            timeseries = self.jdbc_source.get_timeseries(
                filter_id, location_id, parameter_id, start_date, end_date)
            if timeseries:
                is_empty = False
            # Plot data if available.
            dates = [row['time'] for row in timeseries]
            values = [row['value'] for row in timeseries]
            if values:
                graph.axes.plot(dates, values,
                                lw=1,
                                color=line_styles[str(identifier)]['color'],
                                label=location_name)
            # Apply custom layout parameters.
            if 'layout' in identifier:
                layout = identifier['layout']
                title, y_min, y_max, legend = apply_layout(
                    layout, title, y_min, y_max, legend)
                apply_lines(identifier, values, location_name)

        if is_empty and raise_404_if_empty:
            raise Http404

        if identifiers:
            layout = identifiers[0].get('layout')
            if layout:
                if layout.get('legend'):
                    # Ok, this 'if' tree is a bit rediculously deep.
                    #graph.legend(force_legend_below=True)
                    graph.legend()
                    # If there is not data, graph.axes.legend_ is None
                    if graph.axes.legend_ is not None:
                        graph.axes.legend_.draw_frame(False)

        # Extra layout parameters. From lizard-fewsunblobbed.
        if y_min is None:
            y_min, _ = graph.axes.get_ylim()
        if y_max is None:
            _, y_max = graph.axes.get_ylim()

        if layout_extra:
            title, y_min, y_max, legend = apply_layout(
                layout_extra, title, y_min, y_max, legend)

        if title:
            graph.suptitle(title)

        # TODO: set_ylim does not work.
        graph.axes.set_ylim(y_min, y_max)

        # Copied from lizard-fewsunblobbed.
        if "horizontal_lines" in layout_extra:
            for horizontal_line in layout_extra['horizontal_lines']:
                graph.axes.axhline(
                    horizontal_line['value'],
                    ls=horizontal_line['style']['linestyle'],
                    color=horizontal_line['style']['color'],
                    lw=horizontal_line['style']['linewidth'],
                    label=horizontal_line['name'])

        graph.add_today()
        return graph.http_png()

    def symbol_url(self, identifier=None, start_date=None, end_date=None):
        """
        returns symbol

        TODO: the identifier is always None, so individual symbols
        cannot be retrieved.
        """
        _, output_filename = fews_symbol_name(
            self.jdbc_source, self.filterkey, '',
            self.parameterkey, nodata=False)
        return '%sgenerated_icons/%s' % (settings.MEDIA_URL, output_filename)

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        """Overridden so we can put a description of parameter and
        filter in the popup title."""

        extra_kwargs = {
            'parameter':
                self.jdbc_source.get_parameter_name(self.parameterkey),
            'filter': self.jdbc_source.get_filter_name(self.filterkey)
            }

        return super(FewsJdbc, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options,
            template='lizard_fewsjdbc/popup.html',
            extra_render_kwargs=extra_kwargs)
