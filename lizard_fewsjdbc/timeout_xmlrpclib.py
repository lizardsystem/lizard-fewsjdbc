# This code is almost verbatim from:
# http://blog.bjola.ca/2007/08/using-timeout-with-xmlrpclib.html
try:
    import xmlrpclib
    from xmlrpclib import *
except ImportError:
    # Python 3.0 portability fix...
    import xmlrpc.client as xmlrpclib
    from xmlrpc.client import *

import httplib
import socket

class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
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


class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 *args, **kwargs):
        kwargs['transport'] = TimeoutTransport(
            timeout=timeout,
            use_datetime=kwargs.get('use_datetime', 0)
        )
        xmlrpclib.ServerProxy.__init__(self, uri, *args, **kwargs)

ServerProxy = TimeoutServerProxy
