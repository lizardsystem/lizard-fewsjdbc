import copy
import logging
import mapnik
import os

from django.conf import settings
from django.core.cache import cache

from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.operations import named_list
from lizard_map import coordinates
from lizard_map import workspace
from lizard_map.models import ICON_ORIGINALS
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
        icon_style = copy.deepcopy(LAYER_STYLES[str(filter_.fews_id)])
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

    def layer(self, layer_ids=None, webcolor=None, request=None):
        """Return layer and styles that render points.

        """
        layers = []
        styles = {}
        layer = mapnik.Layer("FEWS JDBC points layer", coordinates.WGS84)

        layer.datasource = mapnik.PointDatasource()
        query = ("select longitude, latitude, location from filters "
                 "where id='%s' and parameterid='%s'" % (self.filterkey, self.parameterkey))

        location_cache_key = LOCATION_CACHE_KEY + '::' + self.filterkey + '::' + self.parameterkey
        named_locations = cache.get(location_cache_key)
        if named_locations is None:
            locations = self.jdbc_source.query(query)
            named_locations = named_list(locations, ['longitude', 'latitude', 'location'])
            cache.set(location_cache_key, named_locations)

        for named_location in named_locations:
            layer.datasource.add_point(
                named_location['longitude'],
                named_location['latitude'],
                'Name',
                'Info')

        point_style = fews_point_style(self.filterkey, nodata=False)
        # generate "unique" point style name and append to layer
        style_name = str("Style with data %s::%s" % (self.filterkey, self.parameterkey))
        styles[style_name] = point_style
        layer.styles.append(style_name)

        layers = [layer, ]
        return layers, styles

    def search(self, google_x, google_y, radius=None):
        """Return list of dict {'distance': <float>, 'timeserie':
        <timeserie>} of closest fews point that matches x, y, radius.

        """
        result = []
        return result
