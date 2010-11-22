"""
disqus-python
~~~~~~~~~~~~~

disqus = DisqusAPI(public=public_key, secret=secret_key, format='json')
disqus.trends.listThreads()

"""
try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('disqusapi').version
except:
    __version__ = 'unknown'

    import httplib
    import simplejson
    import urllib

    INTERFACES = {
        'users': {
            'listActivity': {
                'method': 'GET',
            },
        },
    }

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
            if node:
                tree = tree + (node,)
            self.tree = tree
            self.interface = interface

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

            if 'format' not in kwargs:
                kwargs['format'] = api.format
            if 'api_secret' not in kwargs:
                kwargs['api_secret'] = api.api_secret

            version = kwargs.pop('version', api.version)

            if api.is_secure:
                conn = httplib.HTTPSConnection(SSL_HOST)
            else:
                conn = httplib.HTTPConnection(HOST)

            path = '/api/%s/%s' % (version, '/'.join(self.tree))

            conn.request(resource['method'], path, urllib.urlencode(kwargs), {
                'User-Agent': 'disqus-python/%s' % __version__
            })

            response = conn.getresponse()
            # Let's coerce it to Python
            data = api.formats[kwargs['format']](response.read())

            if response.status != 200:
                raise APIError(data['code'], data['response'])

            return data['response']

    class DisqusAPI(Resource):
        formats = {
            'json': lambda x: simplejson.loads(x),
        }

        def __init__(self, api_secret=None, format='json', version='3.0', is_secure=False):
            self.api_secret = api_secret
            self.format = format
            self.version = version
            self.is_secure = is_secure
            super(DisqusAPI, self).__init__(self)

        def __call__(self, **kwargs):
            raise SyntaxError('You cannot call the API without a resource.')

        def setPublicKey(self, key):
            raise NotImplementedError('You cannot use the public API key server-side.')

        def setSecretKey(self, key):
            self.api_secret = key

        def setFormat(self, format):
            self.format = format