# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.utils.formats import localize
from lizard_fewsjdbc import dtu
from piston.emitters import Emitter

TIMESERIE_HEADERS = ('time', 'value')


class BaseRowEmitter(Emitter):
    """Base class for the csv/html emitters: provide rows and headers."""

    @property
    def extracted(self):
        if not hasattr(self, '_extracted'):
            self._extracted = self.construct()
        return self._extracted

    @property
    def rows(self):
        data = self.extracted['data']
        dtu.astimezone(data)  # UTC => local time
        for timeserie in data:
            row = []
            for key in TIMESERIE_HEADERS:
                row.append(timeserie[key])
            yield row

    @property
    def headers(self):
        result = []
        for header in TIMESERIE_HEADERS:
            if header != 'value':
                result.append(header)
            else:
                result.append(self.extracted['parameter_name'])
        return result


class TimeserieHtmlTableEmitter(BaseRowEmitter):
    """Piston emitter for a plain html table.

    The following settings determine how datetimes are formatted:
    - settings.TIME_ZONE, e.g. 'Europe/Amsterdam'
    - settings.DATETIME_FORMAT_FEWSJDBC, e.g. '%Y-%m-%d %H:%M:%S'

    The following setting determines how values are formatted:
    - settings.USE_L10N, e.g. True or False
    """

    def render(self, request):
        result = []
        result.append('<table><tr>')
        for header in self.headers:
            result.append('<th>%s</th>' % header)
        result.append('</tr>')
        for row in self.rows:
            result.append('<tr><td>%s</td><td>%s</td></tr>'
                % (dtu.asstring(row[0]), localize(row[1])))
        result.append('</table>')
        return '\n'.join(result)


Emitter.register('jdbc_html_table',
                 TimeserieHtmlTableEmitter,
                 'text/html; charset=utf-8')
