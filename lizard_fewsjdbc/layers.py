import copy
import datetime
import logging
import mapnik
import math
import os

from django.conf import settings
from django.core.cache import cache

from lizard_fewsjdbc.models import JdbcSource
from lizard_map import coordinates
from lizard_map import workspace
from lizard_map.adapter import Graph
from lizard_map.models import ICON_ORIGINALS
from lizard_map.operations import named_list
from lizard_map.symbol_manager import SymbolManager

logger = logging.getLogger('lizard_fewsunblobbed.layers')

LOCATION_CACHE_KEY = 'lizard_fewsjdbc.layers.location_cache_key'

LAYER_STYLES = {
    "default": {'icon': 'meetpuntPeil.png',
                'mask': ('meetpuntPeil_mask.png', ),
                'color': (0, 0, 1, 0)},
    "Waterkwaliteit_REST": {'icon': 'meetpuntPeil.png',
                            'mask': ('meetpuntPeil_mask.png', ),
                            'color': (1, 1, 0, 0)},
    }


def fews_symbol_name(filterkey, nodata=False):
    """
    Find fews symbol name.
    Copied from lizard_fewsunblobbed.
    """

    # determine icon layout by looking at filter.id
    if str(filterkey) in LAYER_STYLES:
        icon_style = copy.deepcopy(LAYER_STYLES[str(filterkey)])
    else:
        icon_style = copy.deepcopy(LAYER_STYLES['default'])

    #make icon grey
    if nodata:
        icon_style['color'] = (0.9, 0.9, 0.9, 0)

    # apply icon layout using symbol manager
    symbol_manager = SymbolManager(
        ICON_ORIGINALS,
        os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
    output_filename = symbol_manager.get_symbol_transformed(
        icon_style['icon'], **icon_style)

    return output_filename


def fews_point_style(filterkey, nodata=False):
    """
    Make mapnik point_style for fews point with given filterkey.
    Copied from lizard_fewsunblobbed.
    """
    output_filename = fews_symbol_name(filterkey, nodata)
    output_filename_abs = os.path.join(
        settings.MEDIA_ROOT, 'generated_icons', output_filename)

    # use filename in mapnik pointsymbolizer
    point_looks = mapnik.PointSymbolizer(output_filename_abs, 'png', 16, 16)
    point_looks.allow_overlap = True
    layout_rule = mapnik.Rule()
    layout_rule.symbols.append(point_looks)
    point_style = mapnik.Style()
    point_style.rules.append(layout_rule)

    return point_style


class FewsJdbc(workspace.WorkspaceItemAdapter):
    """
    Registered as adapter_fewsjdbc.
    """

    def __init__(self, *args, **kwargs):
        super(FewsJdbc, self).__init__(
            *args, **kwargs)
        self.jdbc_source_slug = self.layer_arguments['slug']
        self.filterkey = self.layer_arguments['filter']
        self.parameterkey = self.layer_arguments['parameter']

        self.jdbc_source = JdbcSource.objects.get(slug=self.jdbc_source_slug)

    def _locations(self):
        """
        Query locations from jdbc source and return named locations in
        a list.

        {'location': '<location name>', 'longitude': <longitude>,
        'latitude': <latitude>}
        """
        location_cache_key = ('%s::%s::%s' %
                              (LOCATION_CACHE_KEY, self.filterkey,
                               self.parameterkey))
        named_locations = cache.get(location_cache_key)
        if named_locations is None:
            query = ("select longitude, latitude, location, locationid "
                     "from filters "
                     "where id='%s' and parameterid='%s'" %
                     (self.filterkey, self.parameterkey))
            locations = self.jdbc_source.query(query)
            named_locations = named_list(
                locations,
                ['longitude', 'latitude', 'location', 'locationid'])
            cache.set(location_cache_key, named_locations)
        return named_locations

    def layer(self, layer_ids=None, webcolor=None, request=None):
        """Return layer and styles that render points.

        """
        layers = []
        styles = {}
        layer = mapnik.Layer("FEWS JDBC points layer", coordinates.WGS84)

        layer.datasource = mapnik.PointDatasource()

        named_locations = self._locations()

        for named_location in named_locations:
            layer.datasource.add_point(
                named_location['longitude'],
                named_location['latitude'],
                'Name',
                'Info')

        point_style = fews_point_style(self.filterkey, nodata=False)
        # generate "unique" point style name and append to layer
        style_name = str("Style with data %s::%s" %
                         (self.filterkey, self.parameterkey))
        styles[style_name] = point_style
        layer.styles.append(style_name)

        layers = [layer, ]
        return layers, styles

    def extent(self, identifiers=None):
        north = None
        south = None
        east = None
        west = None
        named_locations = self._locations()

        result = []
        for named_location in named_locations:
            x = named_location['longitude']
            y = named_location['latitude']
            if x > east or east is None:
                east = x
            if x < west or west is None:
                west = x
            if y < south or south is None:
                south = y
            if y > north or north is None:
                north = y
        west_transformed, north_transformed = coordinates.wgs84_to_google(
            west, north)
        east_transformed, south_transformed = coordinates.wgs84_to_google(
            east, south)

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
        return result

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

        identifier = {'location': location}
        if layout is not None:
            identifier['layout'] = layout

        x, y = coordinates.wgs84_to_google(
            dict_locations[location]['longitude'],
            dict_locations[location]['latitude'])

        return {
            'name': dict_locations[location]['location'],
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
              layout_extra=None):

        line_styles = self.line_styles(identifiers)

        today = datetime.datetime.now()
        graph = Graph(start_date, end_date,
                      width=width, height=height, today=today)
        graph.axes.grid(True)

        for identifier in identifiers:
            filter_id = self.filterkey
            location_id = identifier['location']
            parameter_id = self.parameterkey
            timeseries = self.jdbc_source.get_timeseries(
                filter_id, location_id, parameter_id, start_date, end_date)

            # Plot data.
            dates = [row['time'] for row in timeseries]
            values = [row['value'] for row in timeseries]
            graph.axes.plot(dates, values,
                            lw=1,
                            color=line_styles[str(identifier)]['color'],
                            label=parameter_id)

        # if legend:
        #     graph.legend()

        graph.add_today()
        return graph.http_png()

    def symbol_url(self, identifier=None, start_date=None, end_date=None):
        """
        returns symbol

        """
        output_filename = fews_symbol_name(self.filterkey, nodata=False)
        return '%sgenerated_icons/%s' % (settings.MEDIA_URL, output_filename)

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        return super(FewsJdbc, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)
