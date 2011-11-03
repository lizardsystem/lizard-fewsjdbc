# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from lizard_fewsjdbc.views import HomepageView, JdbcSourceView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        HomepageView.as_view(),
        name="lizard_fewsjdbc.homepage",
        ),
    url(r'^fews_jdbc/(?P<jdbc_source_slug>.*)/$',
        JdbcSourceView.as_view(),
        name="lizard_fewsjdbc.jdbc_source",
        ),
    (r'^map/', include('lizard_map.urls')),
    (r'^api/', include('lizard_fewsjdbc.api.urls')),
    )


if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
