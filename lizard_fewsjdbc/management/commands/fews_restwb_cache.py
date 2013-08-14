"""

"""

from optparse import make_option
from django.core.management.base import BaseCommand

from lizard_fewsjdbc.tasks import rebuild_restws_cache


class Command(BaseCommand):
    args = ''
    help = '''Populate fews jdbc filter cache for better user experience.
If an argument is given, use that as the URL name for the filter tree's
URLs, or give None as an argument to not generate any URLs.'''

    option_list = BaseCommand.option_list + (
        make_option('--source_code',
                    help='Create cache for this source, '
                    'locations, filters, timeseries, parameters.'),
        make_option('--timeout', '-t', dest='timeout',
                    help='Cache timeout in seconds. Default is 8*60*60'
                    ' = 8 hours.'),
        )

    def handle(self, *args, **options):
        rebuild_restws_cache(None, options.get('source_code'))
