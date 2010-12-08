# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import iso8601
import logging
import xmlrpclib
from xml.parsers.expat import ExpatError
from socket import gaierror

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from lizard_fewsjdbc.operations import named_list
from lizard_fewsjdbc.operations import tree_from_list
from lizard_fewsjdbc.operations import unique_list

JDBC_NONE = -999
JDBC_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FILTER_CACHE_KEY = 'lizard_fewsjdbc.models.filter_cache_key'

logger = logging.getLogger(__name__)


class JdbcSource(models.Model):
    """
    Uses Jdbc2Ei to connect to a Jdbc source. Works only for Jdbc2Ei
    that is connected to a FEWS-JDBC server.
    """

    slug = models.SlugField()
    name = models.CharField(max_length=200)
    jdbc_url = models.URLField(verify_exists=False, max_length=200)
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

    class Meta:
        verbose_name = _("Jdbc Source")
        verbose_name_plural = _("Jdbc Sources")

    def __unicode__(self):
        return u'%s' % self.name

    def query(self, q):
        """
        Tries to connect to the Jdbc source and fire query. Returns
        list of lists.

        Throws (socket.)gaierror if server is not reachable.
        """
        if '"' in q:
            logger.warn(
                "You used double quotes in the query. "
                "Is it intended? Query: %s" % q)
        sp = xmlrpclib.ServerProxy(self.jdbc_url)
        sp.Ping.isAlive('', '')

        # sp.Config.get('', '', self.jdbc_tag_name)
        try:
            # Check if jdbc_tag_name is used
            sp.Config.get('', '', self.jdbc_tag_name)
        except ExpatError:
            sp.Config.put('', '', self.jdbc_tag_name, self.connector_string)

        result = sp.Query.execute('', '', q, [self.jdbc_tag_name])

        return result

    @property
    def _customfilter(self):
        return eval(self.customfilter)

    def get_filter_tree(self,
                        url_name='lizard_fewsjdbc.jdbc_source',
                        ignore_cache=False):
        """
        Gets filter tree from Jdbc source. Also adds url per filter
        which links to url_name.

        [{'name': <name>, 'url': <url>, children: [...]}]

        url, children is optional.

        Uses cache.
        """
        filter_source_cache_key = FILTER_CACHE_KEY + '::' + self.slug
        filter_tree = cache.get(filter_source_cache_key)
        if filter_tree is None:
            # Building up the fews filter tree.
            if self.usecustomfilter:
                named_filters = self._customfilter
                root_parent = None
            else:
                try:
                    filters = self.query(
                        "select id, name, parentid from filters;")
                except gaierror:
                    return [{'name': 'Jdbc2Ei server not available.'}]
                if isinstance(filters, int):
                    logger.error("JdbcSource returned an error: %s" % filters)
                    return [{'name': 'Jdbc data source not available.'}]
                unique_filters = unique_list(filters)
                named_filters = named_list(unique_filters,
                                           ['id', 'name', 'parentid'])
                if self.filter_tree_root:
                    root_parent = self.filter_tree_root
                else:
                    root_parent = JDBC_NONE

            # Add url per filter.
            for named_filter in named_filters:
                url = reverse(url_name,
                              kwargs={'jdbc_source_slug': self.slug})
                url += '?filter_id=%s' % named_filter['id']
                named_filter['url'] = url
            # Make the tree.
            filter_tree = tree_from_list(
                named_filters,
                id_field='id',
                parent_field='parentid',
                children_field='children',
                root_parent=root_parent)

            cache.set(filter_source_cache_key, filter_tree, 8 * 60 * 60)
        return filter_tree

    def get_named_parameters(self, filter_id, ignore_cache=False):
        """
        Get named parameters given filter_id: [{'name': <filter>,
        'parameterid': <parameterid1>, 'parameter': <parameter1>},
        ...]

        Uses cache.
        """
        parameter_cache_key = ('%s::%s::%s' %
                               (FILTER_CACHE_KEY, self.slug, str(filter_id)))
        named_parameters = cache.get(parameter_cache_key)

        if named_parameters is None:
            parameter_result = self.query(
                ("select name, parameterid, parameter "
                 "from filters where id='%s'" % filter_id))
            unique_parameters = unique_list(parameter_result)
            named_parameters = named_list(unique_parameters,
                                          ['name', 'parameterid', 'parameter'])
            cache.set(parameter_cache_key, named_parameters, 8 * 60 * 60)
        return named_parameters

    def get_timeseries(self, filter_id, location_id,
                       parameter_id, start_date, end_date):
        """
        SELECT TIME,VALUE,FLAG,DETECTION,COMMENT from
        ExTimeSeries WHERE filterId = 'MFPS' AND parameterId =
        'H.meting' AND locationId = 'BW_NZ_04' AND time BETWEEN
        '2007-01-01 13:00:00' AND '2008-01-10 13:00:00'
        """
        q = ("select time, value, flag, detection, comment from "
             "extimeseries where filterid='%s' and locationid='%s' "
             "and parameterid='%s' and time between '%s' and '%s'" %
             (filter_id, location_id, parameter_id,
              start_date.strftime(JDBC_DATE_FORMAT),
              end_date.strftime(JDBC_DATE_FORMAT)))
        query_result = self.query(q)
        result = named_list(
            query_result, ['time', 'value', 'flag', 'detection', 'comment'])
        for row in result:
            date_time = row['time'].value
            date_time_adjusted = '%s-%s-%s' % (
                date_time[0:4], date_time[4:6], date_time[6:])
            row['time'] = iso8601.parse_date(date_time_adjusted)
        return result

    def get_unit(self, parameter_id):
        """
        Gets unit for given parameter.

        select unit from parameters where id='<parameter_id>'

        Assumes 1 row is fetched.
        """
        q = ("select unit from parameters where id='%s'" % parameter_id)
        query_result = self.query(q)
        return query_result[0][0]  # First row, first column.
