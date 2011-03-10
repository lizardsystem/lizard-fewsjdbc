"""

"""

from django.core.management.base import BaseCommand, CommandError
import logging

from lizard_fewsjdbc.models import JdbcSource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Populate fews jdbc cache for better user experience'

    def handle(self, *args, **options):
        for jdbc_source in JdbcSource.objects.all():
            logger.info('Processing %s ...' % jdbc_source)
            try:
                jdbc_source.get_filter_tree(ignore_cache=True)
            except:
                logger.warn('Tried %s unsuccessfully.' % jdbc_source)
        logger.info('Finished.')
