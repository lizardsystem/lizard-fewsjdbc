import logging

from lizard_datasource import criteria
from lizard_datasource import datasource
from lizard_datasource import dates
from lizard_datasource import location
from lizard_datasource import properties
from lizard_datasource import timeseries

from lizard_fewsjdbc import models

logger = logging.getLogger(__name__)


class FewsJdbcDataSource(datasource.DataSource):
    PROPERTIES = (
        properties.LAYER_POINTS,
        properties.DATA_CAN_HAVE_VALUE_LAYER_SCRIPT
        )

    def __init__(self, jdbc_source):
        self.jdbc_source = jdbc_source

    @property
    def identifier(self):
        return self.jdbc_source.slug

    @property
    def description(self):
        return self.jdbc_source.name

    @property
    def originating_app(self):
        return 'lizard_fewsjdbc'

    def criteria(self):
        return (
            criteria.AppNameCriterion(),
            criteria.Criterion(
                identifier='jdbc_source_slug',
                description='JDBC Source',
                datatype=criteria.Criterion.TYPE_SELECT,
                prerequisites=()),
            criteria.Criterion(
                identifier='filter',
                description='Filter',
                datatype=criteria.Criterion.TYPE_TREE,
                prerequisites=()),
            criteria.Criterion(
                identifier='parameter',
                description='Parameter',
                datatype=criteria.Criterion.TYPE_SELECT,
                prerequisites=('filter',))
            )

    def _filtertree(self):
        def tree_list(nodes):
            for node in nodes:
                if node['children']:
                    yield criteria.OptionTree(
                        description=node['name'],
                        children=tree_list(node['children']))
                else:
                    yield criteria.OptionTree(
                        option=criteria.Option(node['id'], node['name']))

        filters_to_process = self.jdbc_source.get_filter_tree()

        if not filters_to_process:
            return criteria.EmptyOptions()

        tree = criteria.OptionTree(
            description=None,
            children=list(tree_list(filters_to_process)))

        return tree

    def _parameters(self):
        """We shouldn't get here unless filter has been chosen."""
        if 'filter' not in self._choices_made:
            return criteria.EmptyOptions()

        filter_id = self._choices_made['filter']
        named_parameters = self.jdbc_source.get_named_parameters(filter_id)
        logger.debug("named_parameters: {0}".format(named_parameters))
        if not named_parameters:
            return criteria.EmptyOptions()
        else:
            return criteria.OptionList(
                criteria.Option(p['parameterid'], p['parameter'])
                for p in named_parameters)

    def options_for_criterion(self, criterion):
        if criterion.identifier == 'appname':
            return criteria.OptionList([
                    criteria.Option('lizard_fewsjdbc', 'FEWS JDBC')])
        if criterion.identifier == 'jdbc_source_slug':
            return criteria.OptionList([
                criteria.Option(
                        self.jdbc_source.slug,
                        self.jdbc_source.name)])
        if criterion.identifier == 'filter':
            return self._filtertree()
        if criterion.identifier == 'parameter':
            return self._parameters()
        return criteria.EmptyOptions()

    def is_applicable(self, choices_made):
        if not super(FewsJdbcDataSource, self).is_applicable(choices_made):
            return False

        if ('appname' in choices_made and
            choices_made['appname'] != 'lizard_fewsjdbc'):
            return False
        if ('jdbc_source_slug' in choices_made and
            choices_made['jdbc_source_slug'] != self.jdbc_source.slug):
            return False

        return True

    def is_drawable(self, choices_made):
        return ('filter' in choices_made and 'parameter' in choices_made)

    def locations(self, bare=False):
        if not self.is_drawable(self._choices_made):
            raise ValueError(
                "Datasource locations() called when it wasn't drawable")

        return [
            location.Location(
                identifier=loc['locationid'],
                latitude=loc['latitude'],
                longitude=loc['longitude'],
                description=loc['location'])

            for loc in self.jdbc_source.get_locations(
                self._choices_made['filter'],
                self._choices_made['parameter'])
            ]

    def timeseries(self, location_id, start_datetime=None, end_datetime=None):
        try:
            jdbc_result = self.jdbc_source.get_timeseries(
                self._choices_made['filter'],
                location_id,
                self._choices_made['parameter'],
                start_datetime,
                end_datetime)
        except:
            # Timeouts and such
            jdbc_result = []

        series = dict()
        for point in jdbc_result:
            series[dates.to_utc(point['time'])] = point['value']

        return timeseries.Timeseries(series)


def factory():
    """Returns a fewsjdbc datasource for each JDBC slug."""
    for source in models.JdbcSource.objects.all():
        logger.debug("slug: {0}".format(source.slug))

    try:
        return [FewsJdbcDataSource(source)
                for source in models.JdbcSource.objects.all()]
    except Exception, e:
        logger.debug(e)
        return []