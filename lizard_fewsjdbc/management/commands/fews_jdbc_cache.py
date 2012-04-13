"""

"""

from optparse import make_option

from django.core.management.base import BaseCommand
import logging

from lizard_fewsjdbc.models import JdbcSource
from lizard_fewsjdbc.models import CACHE_TIMEOUT

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = '''Populate fews jdbc filter cache for better user experience.
If an argument is given, use that as the URL name for the filter tree's
URLs, or give None as an argument to not generate any URLs.'''

    option_list = BaseCommand.option_list + (
        make_option('--deep', '-d', dest='deep', action="store_true",
                    help='Create deep cache, besides filters also do '
                    'parameters and locations.'),
        make_option('--timeout', '-t', dest='timeout',
                    help='Cache timeout in seconds. Default is 8*60*60'
                    ' = 8 hours.'),
        )

    def load_parameters(self, jdbc_source, tree, url_name, default_url_name):
        params = []
        for item in tree:
            if item["children"]:
                params.extend(
                    self.load_parameters(
                        jdbc_source, item["children"],
                        url_name, default_url_name))
            else:
                logger.debug("Getting named parameters for %s." %
                             (item["id"],))
                if default_url_name:
                    parameters = jdbc_source.get_named_parameters(
                        item["id"], ignore_cache=True,
                        cache_timeout=self.timeout)
                else:
                    parameters = jdbc_source.get_named_parameters(
                        item["id"], ignore_cache=True, url_name=url_name,
                        cache_timeout=self.timeout)
                for p in parameters:
                    params.append((item["id"], p["parameterid"]))

        logger.debug("PARAMS: " + str(params))
        return params

    def handle(self, *args, **options):
        if options['timeout']:
            self.timeout = int(options['timeout'])
            logger.info("Using a cache timeout of %d seconds." % self.timeout)
        else:
            self.timeout = CACHE_TIMEOUT

        if options['deep']:
            logger.info("Traversing deep tree.")

        for jdbc_source in JdbcSource.objects.all():
            logger.info('Processing %s ...' % jdbc_source)
            if args:
                default_url_name = False
                if args[0] == 'None':
                    url_name = None
                else:
                    url_name = args[0]
            else:
                default_url_name = True
            try:
                if default_url_name:
                    tree = jdbc_source.get_filter_tree(
                        ignore_cache=True, cache_timeout=self.timeout)
                else:
                    tree = jdbc_source.get_filter_tree(
                        ignore_cache=True, url_name=url_name,
                        cache_timeout=self.timeout)

                if options['deep']:
                    if default_url_name:
                        params = self.load_parameters(
                            jdbc_source, tree,
                            default_url_name)
                    else:
                        params = self.load_parameters(
                            jdbc_source, tree,
                            url_name, default_url_name)

                    for filter_id, param_id in params:
                        logger.debug(
                            "Getting locations: %s, %s" %
                            (filter_id, param_id))
                        jdbc_source.get_locations(
                            filter_id, param_id,
                            cache_timeout=self.timeout)

            except Exception as e:
                logger.warn(e)
                logger.warn('Tried %s unsuccessfully.' % jdbc_source)
        logger.info('Finished.')
