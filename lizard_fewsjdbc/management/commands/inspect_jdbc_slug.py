"""

"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import logging

from lizard_fewsjdbc.models import JdbcSource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = '''Given the name of a jdbc source slug, get the filter
    tree and display it.'''

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

    def print_tree(self, tree, depth=0):
        prefix = '    ' * depth
        for node in tree:
            print ("%s%s [%s]" % (prefix, node["name"], node["id"]))
            if node["children"]:
                self.print_tree(node["children"], depth + 1)
            else:
                parameters = self.jdbc_source.get_named_parameters(
                    node["id"], ignore_cache=True)
                for p in parameters:
                    print ("%sP: %s [%s]" %
                           (prefix, p["parameter"], p["parameterid"]))
                pass

    def handle(self, *args, **options):
        if not args:
            slugs = "\n  ".join(
                source.slug for source in JdbcSource.objects.all())
            raise CommandError(
                "No JDBC source slug given. Available slugs:\n" +
                "  " + slugs)

        slug = args[0]

        try:
            self.jdbc_source = JdbcSource.objects.get(slug=slug)
        except JdbcSource.DoesNotExist:
            raise CommandError("JDBC source slug '%s' not configured." % slug)

        try:
            tree = self.jdbc_source.get_filter_tree(ignore_cache=True)
            self.print_tree(tree)

        except Exception as e:
            error = (str(e) +
                     ('\nTried %s unsuccessfully.\n' % self.jdbc_source) +
                     "Finished.")
            raise CommandError(error)
