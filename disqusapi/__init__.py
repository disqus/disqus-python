"""
disqus-python
~~~~~~~~~~~~~

disqus = DisqusAPI(api_secret=secret_key)
disqus.trends.listThreads()

"""
try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('disqusapi').version
except:
    __version__ = 'unknown'

import httplib
import os.path
import simplejson
import urllib

INTERFACES = simplejson.loads(open(os.path.join(os.path.dirname(__file__), 'interfaces.json'), 'r').read())

HOST = 'disqus.com'
SSL_HOST = 'secure.disqus.com'

class InterfaceNotDefined(NotImplementedError): pass
class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

class Resource(object):
    def __init__(self, api, interface=INTERFACES, node=None, tree=()):
        self.api = api
        self.node = node
        self.interface = interface
        if node:
            tree = tree + (node,)
        self.tree = tree

    def __getattr__(self, attr):
        if attr in getattr(self, '__dict__'):
            return getattr(self, attr)
        interface = self.interface
        if attr not in interface:
            raise InterfaceNotDefined(attr)
        return Resource(self.api, interface[attr], attr, self.tree)

    def __call__(self, **kwargs):
        # Handle undefined interfaces

        resource = self.interface
        for k in resource.get('required', []):
            if not kwargs.get(k):
                raise ValueError('Missing required argument: %s' % k)

        api = self.api

        if 'api_secret' not in kwargs:
            kwargs['api_secret'] = api.key

        version = kwargs.pop('version', api.version)
        format = kwargs.pop('format', api.format)

        if api.is_secure:
            conn = httplib.HTTPSConnection(SSL_HOST)
        else:
            conn = httplib.HTTPConnection(HOST)

        path = '/api/%s/%s.%s' % (version, '/'.join(self.tree), format)

        # We need to ensure this is a list so that
        # multiple values for a key work
        qs = []
        for k, v in kwargs.iteritems():
            if isinstance(v, (list, tuple)):
                for val in v:
                    qs.append((k, val))
            else:
                qs.append((k, v))

        if resource['method'] == 'GET':
            path = '%s?%s' % (path, urllib.urlencode(qs))
            data = {}
        else:
            data = urllib.urlencode(qs)

        conn.request(resource['method'], path, data, {
            'User-Agent': 'disqus-python/%s' % __version__
        })

        response = conn.getresponse()
        # Let's coerce it to Python
        data = api.formats[format](response.read())

        if response.status != 200:
            raise APIError(data['code'], data['response'])

        return data['response']

class DisqusAPI(Resource):
    formats = {
        'json': lambda x: simplejson.loads(x),
    }

    def __init__(self, key=None, format='json', version='3.0', is_secure=False):
        self.key = key
        self.format = format
        self.version = version
        self.is_secure = is_secure
        super(DisqusAPI, self).__init__(self)

    def __call__(self, **kwargs):
        raise SyntaxError('You cannot call the API without a resource.')

    def setPublicKey(self, key):
        raise NotImplementedError('You cannot use the public API key server-side.')

    def setKey(self, key):
        self.key = key

    def setFormat(self, format):
        self.format = format

    def setVersion(self, version):
        self.version = version