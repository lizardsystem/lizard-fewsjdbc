# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models
from django.utils.translation import ugettext as _


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
