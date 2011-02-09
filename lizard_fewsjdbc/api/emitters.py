# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import csv

from django.http import HttpResponse
from piston.emitters import Emitter

TIMESERIE_HEADERS = ('time', 'value')


class BaseRowEmitter(Emitter):

    def rows(self):
        data = self.construct()['data']
        for timeserie in data:
            row = []
            for key in TIMESERIE_HEADERS:
                row.append(timeserie[key])
            yield row


class TimeserieCsvEmitter(BaseRowEmitter):

    def render(self, request):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=timeseries.csv'
        
        writer = csv.writer(response)
        writer.writerow(TIMESERIE_HEADERS)
        for row in self.rows():
            writer.writerow(row)
        
        return response        


class TimeserieHtmlTableEmitter(BaseRowEmitter):

    def render(self, request):
        result = []
        result.append('<table><tr>')
        for header in TIMESERIE_HEADERS:
            result.append('<th>%s</th>' % header)
        result.append('</tr>')
        for row in self.rows():
            result.append('<tr><td>%s</td><td>%s</td></tr>' % (row[0], row[1]))
        result.append('</table>')
        return '\n'.join(result)


Emitter.register('jdbc_csv', TimeserieCsvEmitter, 'text/csv; charset=utf-8')
Emitter.register('jdbc_html_table', TimeserieHtmlTableEmitter, 'text/html; charset=utf-8')
