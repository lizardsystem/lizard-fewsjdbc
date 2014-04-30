# This code is almost verbatim from:
# http://blog.bjola.ca/2007/08/using-timeout-with-xmlrpclib.html
try:
    import xmlrpclib
except ImportError:
    # Python 3.0 portability fix...
    import xmlrpc.client as xmlrpclib

import datetime
import httplib
import logging
import re
import socket
import time

import pytz

logger = logging.getLogger(__name__)

TIMESERIES_REGEX = re.compile(r"""
<array><data><value><dateTime.iso8601>     # Opening sequence
(?P<timestamp>[^<]+)                  # 20140429T00:00:00Z
</dateTime.iso8601></value><value><double>
(?P<value>[^<]+)                      # -0.908
</double></value></data></array>
""", re.VERBOSE)


class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.is_timeseries_query = False
        self.timeout = timeout

    def make_connection(self, host):
        #return an existing connection if possible.  This allows
        #HTTP/1.1 keep-alive.
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # create a HTTP connection object from a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        #store the host argument along with the connection object
        self._connection = host, httplib.HTTPConnection(
            chost,
            timeout=self.timeout
        )
        return self._connection[1]

    def parse_response(self, response):
        if not self.is_timeseries_query:
            return xmlrpclib.Transport.parse_response(self, response)
        # Special timeseries handling: brute-force regex!
        return self.parse_timeseries_response(response)

    def parse_timeseries_response(self, response):
        # Check for new http response object, else it is a file object
        if hasattr(response,'getheader'):
            if response.getheader("Content-Encoding", "") == "gzip":
                stream = xmlrpclib.GzipDecodedResponse(response)
            else:
                stream = response
        else:
            stream = response

        t1 = time.time()
        whole_string = stream.read()
        t2 = time.time()
        result = list(extract_times_and_values(whole_string))
        t3 = time.time()
        logger.debug("""Reading and parsing timeseries:
        response size: %s mb
        response reading time from network  : %s ms
        response regex+datetime parsing time: %s ms
        total time:                           %s ms
        number of times and values: %s
        """,
                     len(whole_string) / 1000.0 / 1000.0,
                     round(1000 * (t2 - t1)),
                     round(1000 * (t3 - t2)),
                     round(1000 * (t3 - t1)),
                     len(result))
        return result


def extract_times_and_values(whole_string):
    for match in re.finditer(TIMESERIES_REGEX, whole_string):
        timestamp = match.group('timestamp')
        # Expecting 20140424T01:00:00Z
        datetime_format = "%Y%m%dT%H:%M:%SZ"
        timestamp = datetime.datetime.strptime(
            timestamp, datetime_format).replace(
                    tzinfo=pytz.UTC)
        yield(dict(time=timestamp,
                   value=float(match.group('value'))))


class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 *args, **kwargs):
        if 'transport' not in kwargs:
            kwargs['transport'] = TimeoutTransport(
                timeout=timeout,
                use_datetime=kwargs.get('use_datetime', 0)
            )
        xmlrpclib.ServerProxy.__init__(self, uri, *args, **kwargs)

    def mark_as_timeseries_query(self):
        self._ServerProxy__transport.is_timeseries_query = True


ServerProxy = TimeoutServerProxy
