import sys

PY3 = sys.version_info[0] == 3

if PY3:
    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    xrange = range

    import http.client as http_client  # NOQA
    import urllib.parse as urllib_parse  # NOQA
else:
    def iterkeys(d, **kw):
        return iter(d.iterkeys(**kw))

    def iteritems(d, **kw):
        return iter(d.iteritems(**kw))

    xrange = xrange

    import httplib as http_client  # NOQA
    import urllib as urllib_parse  # NOQA
