"""

"""

from optparse import make_option
from django.core.management.base import BaseCommand

from lizard_fewsjdbc.tasks import rebuild_jdbc_cache


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

    def handle(self, *args, **options):
        rebuild_jdbc_cache(*args, **options)
