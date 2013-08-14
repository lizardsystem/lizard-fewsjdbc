from django.contrib import admin
from lizard_fewsjdbc.models import (
    IconStyle,
    JdbcSource,
    Threshold,
    WebRSSource
)


class JdbcSourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'filter_tree_root')


class IconStyleAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'jdbc_source', 'fews_filter', 'fews_location',
        'fews_parameter', 'icon', 'color')
    list_filter = (
        'jdbc_source', 'fews_filter', 'fews_location',
        'fews_parameter', 'icon', 'color')


class ThresholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'filter_id', 'parameter_id', 'location_id',
        'value')


class WebRSSourceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'version', 'base_path')


admin.site.register(JdbcSource, JdbcSourceAdmin)
admin.site.register(IconStyle, IconStyleAdmin)
admin.site.register(Threshold, ThresholdAdmin)
admin.site.register(WebRSSource, WebRSSourceAdmin)
