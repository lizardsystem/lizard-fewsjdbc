from django.contrib import admin
from lizard_fewsjdbc.models import (
    IconStyle,
    IconStyleWebRS,
    JdbcSource,
    Threshold,
    WebRSSource,
    FilterCache,
    LocationCache,
    ParameterCache,
    TimeseriesCache
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


class IconStyleWebRSAdmin(admin.ModelAdmin):
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
    list_display = ('name', 'slug', 'version', 'base_path')


admin.site.register(JdbcSource, JdbcSourceAdmin)
admin.site.register(IconStyle, IconStyleAdmin)
admin.site.register(IconStyleWebRS, IconStyleWebRSAdmin)
admin.site.register(Threshold, ThresholdAdmin)
admin.site.register(WebRSSource, WebRSSourceAdmin)
admin.site.register(FilterCache)
admin.site.register(LocationCache)
admin.site.register(ParameterCache)
admin.site.register(TimeseriesCache)
