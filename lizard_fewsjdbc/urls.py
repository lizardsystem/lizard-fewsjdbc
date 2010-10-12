# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        'lizard_fewsjdbc.views.homepage',
        name="lizard_fewsjdbc.homepage",
        ),
    url(r'^fews_jdbc/(?P<jdbc_source_slug>.*)/$',
        'lizard_fewsjdbc.views.jdbc_source',
        name="lizard_fewsjdbc.jdbc_source",
        ),
    (r'^map/', include('lizard_map.urls')),
    )


if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
