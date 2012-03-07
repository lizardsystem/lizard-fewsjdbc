"""

"""

from django.core.management.base import BaseCommand
import logging

from lizard_fewsjdbc.models import JdbcSource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = '''Populate fews jdbc filter cache for better user experience.
If an argument is given, use that as the URL name for the filter tree's
URLs, or give None as an argument to not generate any URLs.'''

    def handle(self, *args, **options):
        for jdbc_source in JdbcSource.objects.all():
            logger.info('Processing %s ...' % jdbc_source)
            try:
                if args:
                    if args[0] == 'None':
                        url_name = None
                    else:
                        url_name = args[0]
                    jdbc_source.get_filter_tree(ignore_cache=True,
                                                url_name=url_name)
                else:
                    # Use default
                    jdbc_source.get_filter_tree(ignore_cache=True)
            except:
                logger.warn('Tried %s unsuccessfully.' % jdbc_source)
        logger.info('Finished.')
