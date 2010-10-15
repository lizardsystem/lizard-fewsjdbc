from django.contrib import admin
from lizard_fewsjdbc.models import JdbcSource


class JdbcSourceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'usecustomfilter')


admin.site.register(JdbcSource, JdbcSourceAdmin)
