# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls import url, patterns, include
from django.conf import settings
from django.contrib import admin

from lizard_fewsjdbc.views import (HomepageView, JdbcSourceView,
                                   WebRSSourceView, HomepageViewWebRS,
                                   ThresholdsView, ThresholdUpdateView,
                                   ThresholdDeleteView, ThresholdCreateView)

urlpatterns = patterns(
    '',
    url(r'^$',
        HomepageView.as_view(),
        name="lizard_fewsjdbc.homepage",
        ),
    url(r'^webrs/$',
        HomepageViewWebRS.as_view(),
        name="lizard_fewsjdbc.homepage_webrs",
        ),
    url(r'^webrs/(?P<webrs_source_slug>.*)/$',
        WebRSSourceView.as_view(),
        name="lizard_fewsjdbc.webrs_source",
        ),
    url(r'^fews_jdbc/(?P<jdbc_source_slug>.*)/$',
        JdbcSourceView.as_view(),
        name="lizard_fewsjdbc.jdbc_source",
        ),
    (r'^api/', include('lizard_fewsjdbc.api.urls')),
    # threshold urls
    url(r'^thresholds/create/$', ThresholdCreateView.as_view(),
        name="lizard_fewsjdbc.threshold_create"),
    url(r'^thresholds/update/$', ThresholdUpdateView.as_view(),
        name="lizard_fewsjdbc.threshold_update"),
    url(r'^thresholds/delete/(?P<pk>\d+)/$', ThresholdDeleteView.as_view(),
        name="lizard_fewsjdbc.threshold_delete"),
    url(r'^thresholds/$', ThresholdsView.as_view(),
        name="lizard_fewsjdbc.thresholds"),
)

if getattr(settings, 'LIZARD_FEWSJDBC_STANDALONE', False):
    admin.autodiscover()
    urlpatterns += patterns(
        '',
        (r'^map/', include('lizard_map.urls')),
        (r'^ui/', include('lizard_ui.urls')),
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
