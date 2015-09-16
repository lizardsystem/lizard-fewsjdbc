# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime
import hashlib
import logging
import time

from django.core.cache import cache
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from lizard_map.fields import ColorField
from lizard_map.operations import named_list
from lizard_map.operations import tree_from_list
from lizard_map.operations import unique_list
from lizard_map.symbol_manager import list_image_file_names
from lizard_map.utility import get_host
from lizard_map.views import get_view_state
from pytz import UnknownTimeZoneError
from socket import gaierror
from tls import request as tls_request
from xml.parsers.expat import ExpatError
import pytz

from lizard_fewsjdbc import timeout_xmlrpclib
from lizard_fewsjdbc.utils import format_number

JDBC_NONE = -999
JDBC_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FILTER_CACHE_KEY = 'lizard_fewsjdbc.models.filter_cache_key'
PARAMETER_NAME_CACHE_KEY = 'lizard_fewsjdbc.models.parameter_name_cache_key'
LOCATION_CACHE_KEY = 'lizard_fewsjdbc.layers.location_cache_key'
CACHE_TIMEOUT = 8 * 60 * 60  # Default is 8 hours
LOG_JDBC_QUERIES = True

logger = logging.getLogger(__name__)


class FewsJdbcNotAvailableError(gaierror):
    """Wrapping of generic socket.gaierror into a clearer error."""
    def __str__(self):
        return 'FEWS Jdbc not available. ' + gaierror.__str__(self)


class FewsJdbcQueryError(Exception):
    """Proper exception instead of -1 or -2 ints that the query returns."""
    def __init__(self, value, query=None, connector_string=None):
        self.value = value
        self.query = query
        self.connector_string = connector_string

    def __str__(self):
        return 'The FEWS jdbc query [%s] to [%s] returned error code %s' % (
            self.query, self.connector_string, self.value)


def lowest_filters(id_value, tree, below_id_value=False):
    """Return all ids from descendants from id_value without children.

    Input is a hierarchical tree structure with at least 'id' and
    'children'.
    """
    result = []
    for child in tree:
        if below_id_value:
            below_id = True
        else:
            if id_value == child['id']:
                below_id = True
            else:
                below_id = False
        result += lowest_filters(
            id_value, child['children'],
            below_id_value=below_id)
        if not child['children'] and below_id:
            result += [child['id'], ]

    return result


class JdbcSource(models.Model):
    """
    Uses Jdbc2Ei to connect to a Jdbc source. Works only for Jdbc2Ei
    that is connected to a FEWS-JDBC server.
    """

    slug = models.SlugField()
    name = models.CharField(max_length=200)
    jdbc_url = models.URLField(max_length=200)
    jdbc_tag_name = models.CharField(max_length=80)
    connector_string = models.CharField(max_length=200)

    filter_tree_root = models.CharField(
        max_length=80,
        blank=True, null=True,
        help_text=("Fill in the filter id to use as filter root. "
                   "Only works if no usecustomfilter."))
    usecustomfilter = models.BooleanField(default=False)
    customfilter = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "Use a pythonic list of dictionaries. "
            "The rootnode has 'parentid': None. i.e. "
            "[{'id':'id','name':'name','parentid':None}, "
            "{'id':'id2','name':'name2','parentid':'id'}]"))

    timezone_string = models.CharField(
        max_length=40, default="", blank=True,
        help_text=("""
            Time zone of the datetimes coming from FEWS. Use this only
            if the information coming from FEWS itself is
            incorrect. An empty string means we trust FEWS. A few
            possibilities are UTC, CET (Dutch winter time), CEST
            (Dutch summer time) and Europe/Amsterdam (Dutch local time
            switching between summer and winter time).
        """))

    class Meta:
        verbose_name = _("Jdbc source")
        verbose_name_plural = _("Jdbc sources")

    def __unicode__(self):
        return u'%s' % self.name

    def query(self, q, is_timeseries_query=False):
        """
        Tries to connect to the Jdbc source and fire query. Returns
        list of lists.

        Throws FewsJdbcQueryError if the server is not reachable and a
        FewsJdbcQueryError if the jdbc server returns a ``-1`` or
        ``-2`` error code.

        """
        if '"' in q:
            logger.warn(
                "You used double quotes in the query. "
                "Is it intended? Query: %s", q)
        t1 = time.time()
        try:
            sp = timeout_xmlrpclib.ServerProxy(self.jdbc_url, timeout=30)
            # For debugging: add 'verbose=True' in the line above. This prints
            # ALL the output.
            sp.Ping.isAlive('', '')
        except gaierror, e:
            # Re-raise as more recognizable error.
            raise FewsJdbcNotAvailableError(e)
        t2 = time.time()

        try:
            # Check if jdbc_tag_name is used
            sp.Config.get('', '', self.jdbc_tag_name)
        except ExpatError:
            sp.Config.put('', '', self.jdbc_tag_name, self.connector_string)

        t3 = time.time()
        if is_timeseries_query:
            sp.mark_as_timeseries_query()
        result = sp.Query.execute('', '', q, [self.jdbc_tag_name])
        t4 = time.time()

        if isinstance(result, int):
            raise FewsJdbcQueryError(result, q, self.connector_string)
        if result == [-2]:
            logger.warn("Should not happen. Reinout wants this 'if' "
                        "removed if it doesn't occur in sentry.")
            raise FewsJdbcQueryError(result, q, self.connector_string)
        if LOG_JDBC_QUERIES:
            ping_time = round(1000 * (t2 - t1))
            tag_check_time = round(1000 * (t3 - t2))
            query_time = round(1000 * (t4 - t3))
            total_time = round(1000 * (t4 - t1))
            logger.debug("%dms (%d ping, %d tag check, %d query):\n    %s",
                         total_time, ping_time, tag_check_time, query_time, q)
        return result

    @property
    def _customfilter(self):
        return eval(self.customfilter)

    def get_filter_tree(self,
                        url_name='lizard_fewsjdbc.jdbc_source',
                        ignore_cache=False,
                        cache_timeout=CACHE_TIMEOUT):
        """
        Gets filter tree from Jdbc source. Also adds url per filter
        which links to url_name.

        [{'name': <name>, 'url': <url>, children: [...]}]

        url, children is optional. If url_name is set to None, no url
        property will be set in the filter tree (useful if the
        standard fewsjdbc urls don't exist, for instance when only the
        REST API is used).

        Uses cache unless ignore_cache == True. cache_timeout gives
        an alternative timeout duration for the cache, in seconds.
        """

        filter_source_cache_key = '%s::%s::%s::%s' % (
            url_name, FILTER_CACHE_KEY, self.slug, get_host())
        filter_tree = cache.get(filter_source_cache_key)
        if filter_tree is None or ignore_cache:
            # Building up the fews filter tree.
            if self.usecustomfilter:
                named_filters = self._customfilter
                root_parent = None
            else:
                try:
                    filters = self.query(
                        "select distinct id, name, parentid from filters;")
                except FewsJdbcNotAvailableError, e:
                    return [{'name': _('Jdbc2Ei server not available.'),
                             'error': e}]
                except FewsJdbcQueryError, e:
                    logger.error("JdbcSource returned an error: %s", e,
                                 extra={'jdbc_url': e.jdbc_url})
                    # ^^^ 'extra' ends up as tags in sentry.
                    return [{'name': 'Jdbc data source not available.',
                             'error code': e}]

                unique_filters = unique_list(filters)
                named_filters = named_list(unique_filters,
                                           ['id', 'name', 'parentid'])
                if self.filter_tree_root:
                    root_parent = self.filter_tree_root
                else:
                    root_parent = JDBC_NONE

            # Add url per filter. Only if url_name is actually present.
            if url_name:
                for named_filter in named_filters:
                    url = reverse(url_name,
                                  kwargs={'jdbc_source_slug': self.slug})
                    url += '?filter_id=%s' % named_filter['id']

                    # There used to be a line here that added
                    # 'ignore_cache=True' to the URL if ignore_cache
                    # is true. However, the variable controls whether
                    # we currently ignore the cache, not whether the
                    # URLs we build ignore it. In normal
                    # circumstances, the cache should not be ignored.

                    named_filter['url'] = url
            # Make the tree.
            filter_tree = tree_from_list(
                named_filters,
                id_field='id',
                parent_field='parentid',
                children_field='children',
                root_parent=root_parent)

            if filter_tree:
                # Only cache it when we actually get a tree. Otherwise a
                # one-time fewsjdbc error can propagate.
                cache.set(filter_source_cache_key, filter_tree, cache_timeout)
        return filter_tree

    def get_named_parameters(self, filter_id, ignore_cache=False,
                             find_lowest=True,
                             url_name='lizard_fewsjdbc.jdbc_source',
                             cache_timeout=CACHE_TIMEOUT):
        """
        Get named parameters given filter_id: [{'name': <filter>,
        'parameterid': <parameterid1>, 'parameter': <parameter1>},
        ...]

        The parameters are parameters from the lowest filter below
        given filter_id.

        If find_lowest is True, then this function first searches for
        all the leaf filter nodes below this one, and then returns the
        parameters of those. If find_lowest is set to False (for
        instance because filter_id is already known to be a leaf),
        only parameters directly connected to this filter are
        returned.

        Uses cache unless ignore_cache == True. cache_timeout gives
        an alternative timeout duration for the cache, in seconds.
        """
        parameter_cache_key = ('%s::%s::%s::%s' %
                               (FILTER_CACHE_KEY, self.slug, str(filter_id),
                                get_host()))
        named_parameters = cache.get(parameter_cache_key)

        if find_lowest:
            filter_names = lowest_filters(
                filter_id, self.get_filter_tree(url_name=url_name))
        else:
            filter_names = (filter_id,)

        filter_query = " or ".join(
            ["id='%s'" % filter_name for filter_name in filter_names])

        if ignore_cache or named_parameters is None:
            parameter_result = self.query(
                ("select name, parameterid, parameter, id "
                 "from filters where %s" % filter_query))
            unique_parameters = unique_list(parameter_result)
            named_parameters = named_list(
                unique_parameters,
                ['filter_name', 'parameterid', 'parameter', 'filter_id'])
            if named_parameters:
                # Only cache it when we actually get parameters. Otherwise a
                # one-time fewsjdbc error can propagate.
                cache.set(parameter_cache_key, named_parameters, cache_timeout)

        return named_parameters

    def get_filter_name(self, filter_id):
        """Return the filter name corresponding to the given filter
        id."""
        cache_key = 'filter_name:%s:%s:%s' % (get_host(), filter_id, self.slug)
        result = cache.get(cache_key)
        if result is None:
            result = self.query("select distinct name from filters where id='%s'"
                                % (filter_id,))
            if result:
                result = result[0][0]
                cache.set(cache_key, result, 60 * 60)
        return result

    def get_parameter_name(self, parameter_id):
        """Return parameter name corresponding to the given parameter
        id."""
        cache_key = 'parameter_name:%s:%s:%s' % (get_host(), parameter_id, self.slug)
        result = cache.get(cache_key)
        if result is None:
            result = self.query(("select distinct parameter from filters where " +
                                 "parameterid = '%s'") % (parameter_id,))
            if result:
                result = result[0][0]
                cache.set(cache_key, result, 60 * 60)
        return result

    def get_locations(self, filter_id, parameter_id,
                      cache_timeout=CACHE_TIMEOUT):
        """
        Query locations from jdbc source and return named locations in
        a list.

        {'location': '<location name>', 'longitude': <longitude>,
        'latitude': <latitude>}

        cache_timeout gives an alternative timeout duration for the
        cache, in seconds.
        """
        location_cache_key = ('%s::%s::%s::%s' %
                              (LOCATION_CACHE_KEY, filter_id,
                               parameter_id, get_host()))
        named_locations = cache.get(location_cache_key)
        if named_locations is None:
            query = ("select longitude, latitude, "
                     "location, locationid "
                     "from filters "
                     "where id='%s' and parameterid='%s'" %
                     (filter_id, parameter_id))
            locations = self.query(query)
            named_locations = named_list(
                locations,
                ['longitude', 'latitude',
                 'location', 'locationid'])
            if named_locations:
                # Only cache when we actually have found locations. It might
                # otherwise just be fewsjdbc that tricks us with an empty
                # list.
                cache.set(location_cache_key, named_locations, cache_timeout)
        return named_locations

    def location_list(self, filter_id, parameter_id, name=''):
#        query = (
#            "select name, x, y, id "
#            "from locations "
#            "where id='%s' and parameterid='%s' "
#            "and location.name like '%{}%'"
#        ).format(name)
        query = (
            "select locationid, location "
            "from filters "
            "where id='{}' and parameterid='{}' and location like '%{}%'"
        ).format(filter_id, parameter_id, name)
        locations = self.query(query)
        return locations

    def get_timeseries(self, filter_id, location_id, parameter_id,
                       zoom_start_date, zoom_end_date):
        """Wrapper around _get_timeseries() with some date normalization."""
        try:
            view_state = get_view_state(tls_request)
            view_state_start_date = view_state['dt_start']
            view_state_end_date = view_state['dt_end']
            assert view_state_start_date is not None  # Upon first site visit.
        except:  # yes, bare except.
            view_state_start_date = zoom_start_date
            view_state_end_date = zoom_end_date

        date_range_size = zoom_end_date - zoom_start_date
        if date_range_size < datetime.timedelta(days=7):
            # Normalize the start and end date to start at midnight.
            normalized_start_date = datetime.datetime(
                year=zoom_start_date.year,
                month=zoom_start_date.month,
                day=zoom_start_date.day,
                tzinfo=zoom_start_date.tzinfo)
            zoom_end_date_plus_one = zoom_end_date + datetime.timedelta(days=1)
            normalized_end_date = datetime.datetime(
                year=zoom_end_date_plus_one.year,
                month=zoom_end_date_plus_one.month,
                day=zoom_end_date_plus_one.day,
                tzinfo=zoom_end_date_plus_one.tzinfo)
            cache_timeout = 60
        else:
            # Normalize the start and end date to start at start of the month.
            # And do it from the start/end date that's set in the view state.
            normalized_start_date = datetime.datetime(
                year=view_state_start_date.year,
                month=view_state_start_date.month,
                day=1,
                tzinfo=view_state_start_date.tzinfo)
            view_state_end_date_plus_one_month = (view_state_end_date +
                                                  datetime.timedelta(days=30))
            normalized_end_date = datetime.datetime(
                year=view_state_end_date_plus_one_month.year,
                month=view_state_end_date_plus_one_month.month,
                day=1,
                tzinfo=view_state_end_date_plus_one_month.tzinfo)
            if ((view_state_end_date - view_state_start_date)
                < datetime.timedelta(days=60)):
                cache_timeout = 15 * 60
            else:
                cache_timeout = 20 * 60 * 60

        logger.debug("Timeseries req from %s to %s", zoom_start_date, zoom_end_date)
        logger.debug("View state is  from %s to %s", view_state_start_date, view_state_end_date)
        logger.debug("We're querying from %s to %s", normalized_start_date, normalized_end_date)
        CACHE_VERSION = 4
        cache_key = ':'.join(['get_timeseries',
                              str(CACHE_VERSION),
                              str(filter_id),
                              str(location_id),
                              str(self.slug),
                              str(parameter_id),
                              str(normalized_start_date),
                              str(normalized_end_date)])
        cache_key = hashlib.md5(cache_key).hexdigest()
        try:
            big_cache = get_cache('big_cache')
            # This is supposed to be a filesystem cache: for big items.
        except:
            big_cache = cache
        result = big_cache.get(cache_key)
        if result is None:
            logger.debug("Cache miss for %s", cache_key)
            result = self._get_timeseries(filter_id, location_id,
                                          parameter_id, normalized_start_date,
                                          normalized_end_date)
            if result:  # Don't store empty results
                big_cache.set(cache_key, result, cache_timeout)
            logger.debug("Stored the cache for %s", cache_key)
        else:
            logger.debug("Cache hit for %s", cache_key)

        if isinstance(result, dict):
            # Corner case due to xmlrpclib returning lists with len(1) as a
            # value instead.
            result = [result]
        result = [row for row in result
                  if row['time'] >= zoom_start_date and row['time'] <= zoom_end_date]
        if result:
            logger.debug("Start date: %s, first returned result's time: %s",
                         zoom_start_date, result[0]['time'])
        return result

    def _get_timeseries(self, filter_id, location_id,
                       parameter_id, start_date, end_date):
        q = ("select time, value from "
             "extimeseries where filterid='%s' and locationid='%s' "
             "and parameterid='%s' and time between '%s' and '%s'" %
             (filter_id, location_id, parameter_id,
              start_date.strftime(JDBC_DATE_FORMAT),
              end_date.strftime(JDBC_DATE_FORMAT)))
        return self.query(q, is_timeseries_query=True)

    def get_unit(self, parameter_id):
        """
        Gets unit for given parameter.

        select unit from parameters where id='<parameter_id>'

        Assumes 1 row is fetched.
        """
        q = ("select unit from parameters where id='%s'" % parameter_id)
        query_result = self.query(q)
        return query_result[0][0]  # First row, first column.

    def get_name_and_unit(self, parameter_id):
        """
        Gets name and unit for given parameter.

        Assumes 1 row is fetched.
        """
        cache_key = 'name_and_unit:%s:%s:%s' % (get_host(), parameter_id, self.slug)
        result = cache.get(cache_key)
        if result is None:
            q = ("select name, unit from parameters where id='%s'" % parameter_id)
            query_result = self.query(q)
            result = query_result[0]  # First row, first column.
            cache.set(cache_key, result, 60 * 60)
        return result

    def get_absolute_url(self):
        return reverse('lizard_fewsjdbc.jdbc_source',
                       kwargs={'jdbc_source_slug': self.slug})

    @cached_property
    def timezone(self):
        """Return a tzinfo object for the current JDBC source."""
        try:
            return pytz.timezone(self.timezone_string)
        except UnknownTimeZoneError:
            return None


class IconStyle(models.Model):
    """
    Customizable icon styles where all "selector fields" are optional.

    The styles are cached for performance.
    """

    # Selector fields.
    jdbc_source = models.ForeignKey(JdbcSource, null=True, blank=True)
    fews_filter = models.CharField(max_length=40, null=True, blank=True)
    fews_location = models.CharField(max_length=40, null=True, blank=True)
    fews_parameter = models.CharField(max_length=40, null=True, blank=True)

    # Icon properties.
    icon = models.CharField(max_length=40, choices=list_image_file_names())
    mask = models.CharField(max_length=40, choices=list_image_file_names())
    color = ColorField(help_text="Use color format ffffff or 333333")
    draw_in_legend = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Icon style")
        verbose_name_plural = _("Icon styles")

    def __unicode__(self):
        return u'%s' % (self._key)

    @classmethod
    def CACHE_KEY(cls):
        return 'lizard_fewsjdbc.IconStyle.%s' % (get_host(), )

    @cached_property
    def _key(self):
        return '%s::%s::%s::%s' % (
            self.jdbc_source.id if self.jdbc_source else '',
            self.fews_filter,
            self.fews_location,
            self.fews_parameter)

    @classmethod
    def _styles(cls):
        """
        Return styles in a symbol manager style in a dict.

        The dict key consist of
        "jdbc_source_id::fews_filter::fews_location::fews_parameter"
        """
        result = {}
        for icon_style in cls.objects.all():
            result[icon_style._key] = {
                'icon': icon_style.icon,
                'mask': (icon_style.mask, ),
                'color': icon_style.color.to_tuple(),
                'draw_in_legend': icon_style.draw_in_legend
            }
        return result

    @classmethod
    def _lookup(cls):
        """
        Return style lookup dictionary based on class objects.

        This lookup dictionary is cached and it is rebuild every time
        the IconStyle table changes.

        The structure (always) has 4 levels and is used to lookup icon
        styles with fallback in a fast way:

        level 0 (highest) {None: {level1}, <jdbc_source_id>: {level1},
        ... }

        level 1 {None: {level2}, "<fews_filter_id>": {level2}, ...}

        level 2 {None: {level3}, "<fews_location_id>": {level3}, ...}

        level 3 {None: icon_key, "<fews_parameter_id>": icon_key, ...}
        """

        lookup = {}

        # Insert style into lookup
        for style in cls.objects.all():
            level0 = style.jdbc_source.id if style.jdbc_source else None
            level1 = style.fews_filter if style.fews_filter else None
            level2 = style.fews_location if style.fews_location else None
            level3 = (style.fews_parameter
                      if style.fews_parameter else None)
            if level0 not in lookup:
                lookup[level0] = {}
            if level1 not in lookup[level0]:
                lookup[level0][level1] = {}
            if level2 not in lookup[level0][level1]:
                lookup[level0][level1][level2] = {}
            if level3 not in lookup[level0][level1][level2]:
                lookup[level0][level1][level2][level3] = style._key
            # Every 'breach' needs a 'None' / default side.
            if None not in lookup:
                lookup[None] = {}
            if None not in lookup[level0]:
                lookup[level0][None] = {}
            if None not in lookup[level0][level1]:
                lookup[level0][level1][None] = {}
            if None not in lookup[level0][level1][level2]:
                lookup[level0][level1][level2][None] = '%s::%s::%s::' % (
                    level0 if level0 else '',
                    level1 if level1 else '',
                    level2 if level2 else '')
        return lookup

    @classmethod
    def _styles_lookup(cls, ignore_cache=False):
        cache_lookup = cache.get(cls.CACHE_KEY())

        if cache_lookup is None or ignore_cache:
            # Calculate styles and lookup and store in cache.
            styles = cls._styles()
            lookup = cls._lookup()
            cache_timeout = 60 * 60
            cache.set(cls.CACHE_KEY(), (styles, lookup), cache_timeout)
        else:
            # The cache has a 2-tuple (styles, lookup) stored.
            styles, lookup = cache_lookup

        return styles, lookup

    @classmethod
    def style(
        cls,
        jdbc_source, fews_filter,
        fews_location, fews_parameter,
            styles=None, lookup=None, ignore_cache=False):
        """
        Return the best corresponding icon style and return in format:

        'xx::yy::zz::aa',
        {'icon': 'icon.png',
         'mask': 'mask.png',
         'color': (1,1,1,0),
         'draw_in_legend': True
         }
        """
        if styles is None or lookup is None:
            styles, lookup = cls._styles_lookup(ignore_cache)

        try:
            level1 = lookup.get(jdbc_source.id, lookup[None])
            level2 = level1.get(fews_filter, level1[None])
            level3 = level2.get(fews_location, level2[None])
            found_key = level3.get(fews_parameter, level3[None])
            result = styles[found_key]
        except KeyError:
            # Default, this only occurs when '::::::' is not defined
            return '::::::', {
                'icon': 'meetpuntPeil.png',
                'mask': ('meetpuntPeil_mask.png', ),
                'color': (0.0, 0.5, 1.0, 1.0),
                'draw_in_legend': True
            }

        return found_key, result


class Threshold(models.Model):
    """
    Contains threshold information for fews objects. Can be used for showing
    threshold lines in fews objects graphs.

    """
    name = models.CharField(verbose_name=_("name"), max_length=100)
    label = models.CharField(max_length=100, help_text=_("Label on plot."),
                             blank=True, null=True, verbose_name=_("label"))
    filter_id = models.CharField(max_length=100, blank=True, null=True)
    parameter_id = models.CharField(max_length=100, blank=True, null=True)
    location_id = models.CharField(max_length=100, blank=True, null=True)
    value = models.DecimalField(max_digits=16, decimal_places=8,
                                verbose_name=_("value"))
    color = models.CharField(
        verbose_name=_("color"),
        max_length=6,
        help_text="rrggbb kleurcode, dus 000000=zwart, ff0000=rood, enz.",
        default='000000')

    class Meta:
        verbose_name = _("threshold")
        verbose_name_plural = _("thresholds")
        ordering = ('id',)

    @property
    def pretty_value(self):
        return format_number(self.value)

    def __unicode__(self):
        return "%s : %s (id: %s)" % (self.name, self.value, self.id)


# For Django 1.3:
# @receiver(post_save, sender=Setting)
# @receiver(post_delete, sender=Setting)
def icon_style_post_save_delete(sender, **kwargs):
    """
    Invalidates cache after saving or deleting an IconStyle.
    """
    logger.debug('Changed IconStyle. Invalidating cache for %s...',
                 sender.CACHE_KEY())
    cache.delete(sender.CACHE_KEY())


post_save.connect(icon_style_post_save_delete, sender=IconStyle)
post_delete.connect(icon_style_post_save_delete, sender=IconStyle)
