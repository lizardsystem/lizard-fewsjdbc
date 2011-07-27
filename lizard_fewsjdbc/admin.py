from django.contrib import admin
from lizard_fewsjdbc.models import IconStyle
from lizard_fewsjdbc.models import JdbcSource


class JdbcSourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'filter_tree_root')

class IconStyleAdmin(admin.ModelAdmin):
    list_display = (
        'jdbc_source', 'fews_filter', 'fews_location',
        'fews_parameter', 'icon', 'color')
    list_filter = (
        'jdbc_source', 'fews_filter', 'fews_location',
        'fews_parameter', 'icon', 'color')


admin.site.register(JdbcSource, JdbcSourceAdmin)
admin.site.register(IconStyle, IconStyleAdmin)
