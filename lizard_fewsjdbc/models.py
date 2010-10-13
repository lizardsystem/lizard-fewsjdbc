# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import xmlrpclib
from xml.parsers.expat import ExpatError

from django.db import models
from django.utils.translation import ugettext as _

JDBC_NONE = -999


class JdbcSource(models.Model):
    """
    Uses Jdbc2Ei to connect to a Jdbc source.
    """

    class Meta:
        verbose_name = _("Jdbc Source")
        verbose_name_plural = _("Jdbc Sources")

    slug = models.SlugField()
    name = models.CharField(max_length=200)
    jdbc_url = models.URLField(verify_exists=False, max_length=200)
    jdbc_tag_name = models.CharField(max_length=80)
    connector_string = models.CharField(max_length=200)
    usecustomfilter = models.BooleanField(default=False)
    customfilter = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "Use a pythonic list of dictionaries. "
            "The rootnode has 'parentid': None. i.e. "
            "[{'id':'id','name':'name','parentid':None}, "
            "{'id':'id2','name':'name2','parentid':'id'}]"))

    def __unicode__(self):
        return u'%s' % self.name

    def query(self, q):
        """
        Tries to connect to the Jdbc source and fire query. Returns list of lists.
        """
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
