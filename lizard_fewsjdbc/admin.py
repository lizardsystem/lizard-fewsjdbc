from django.contrib import admin
from lizard_fewsjdbc.models import JdbcSource


class JdbcSourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'filter_tree_root')


admin.site.register(JdbcSource, JdbcSourceAdmin)
