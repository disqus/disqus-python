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

class Paginator(object):
    """
    Paginate through all entries:
    
    >>> paginator = Paginator(api.trends.listThreads, forum='disqus')
    >>> for result in paginator:
    >>>     print result
    
    Paginate only up to a number of entries:
    
    >>> for result in paginator(limit=500):
    >>>     print result
    """
    
    def __init__(self, endpoint, **params):
        self.endpoint = endpoint
        self.params = params
    
    def __iter__(self):
        for result in self():
            yield result
    
    def __call__(self, limit=None):
        params = self.params.copy()
        num = 0
        more = True
        results = self.endpoint(**params)
        while more and (not limit or num < limit):
            for result in results:
                if limit and num >= limit:
                    break
                num += 1
                yield result

            if results.cursor:
                more = results.cursor['more']
                params['cursor'] = results.cursor['id']
            else:
                more = False

class InterfaceNotDefined(NotImplementedError): pass
class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

class Result(object):
    def __init__(self, response, cursor=None):
        self.response = response
        self.cursor = cursor or {}

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, repr(self.response))
    
    def __iter__(self):
        for r in self.response:
            yield r
    
    def __len__(self):
        return len(self.response)
    
    def __getslice__(self, i, j):
        return list.__getslice__(self.response, i, j)
    
    def __getitem__(self, key):
        return list.__getitem__(self.response, key)

    def __contains__(self, key):
        return list.__contains__(self.response, key)
    
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
            data = ""
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

        return Result(data['response'], data.get('cursor'))

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