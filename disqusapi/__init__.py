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
    import simplejson
    import urllib

    INTERFACES = {
        'blacklists': {
            'add': {
                'method': 'POST',
                'required': ['type', 'value']
            },
            'list': {
                'method': 'GET',
            },
            'remove': {
                'method': 'POST',
                'required': ['type', 'value']
            },
        },
        'categories': {
            'details': {
                'method': 'GET',
                'required': ['category'],
            },
            'listPosts': {
                'method': 'GET',
                'required': ['category'],
            },
            'listThreads': {
                'method': 'GET',
                'required': ['category'],
            },
        },
        'forums': {
            'details': {
                'method': 'GET',
                'required': ['forum'],
            },
            'listCategories': {
                'method': 'GET',
                'required': ['forum'],
            },
            'listPosts': {
                'method': 'GET',
                'required': ['forum'],
            },
            'listThreads': {
                'method': 'GET',
                'required': ['forum'],
            },
            'listUsers': {
                'method': 'GET',
                'required': ['forum'],
            },
        },
        'posts': {
            'approve': {
                'method': 'POST',
                'required': ['post'],
            },
            'create': {
                'method': 'POST',
                'required': ['thread', 'message'],
            },
            'details': {
                'method': 'GET',
                'required': ['post'],
            },
            'list': {
                'method': 'GET',
            },
            'listPopular': {
                'method': 'GET',
            },
            'remove': {
                'method': 'POST',
                'required': ['post'],
            },
            'report': {
                'method': 'POST',
                'required': ['post'],
            },
            'restore': {
                'method': 'POST',
                'required': ['post'],
            },
            'spam': {
                'method': 'POST',
                'required': ['post'],
            },
            'update': {
                'method': 'POST',
                'required': ['post'],
            },
            'vote': {
                'method': 'POST',
                'required': ['post', 'vote'],
            },
        },
        'reactions': {
            'details': {
                'method': 'GET',
                'required': ['reaction'],
            },
            'list': {
                'method': 'GET',
            },
        },
        'reports': {
            'domains': {
                'method': 'GET',
            },
            'ips': {
                'method': 'GET',
            },
            'threads': {
                'method': 'GET',
            },
            'users': {
                'method': 'GET',
            },
        },
        'threads': {
            'close': {
                'method': 'POST',
                'required': ['thread'],
            },
            'details': {
                'method': 'GET',
                'required': ['thread'],
            },
            'list': {
                'method': 'GET',
            },
            'listHot': {
                'method': 'GET',
            },
            'listPopular': {
                'method': 'GET',
            },
            'listPosts': {
                'method': 'GET',
            },
            'open': {
                'method': 'POST',
                'required': ['thread'],
            },
            'vote': {
                'method': 'POST',
                'required': ['thread', 'vote'],
            },
        },
        'threads': {
            'listThreads': {
                'method': 'GET',
            },
        },
        'users': {
            'details': {
                'method': 'GET',
            },
            'listActiveForums': {
                'method': 'GET',
            },
            'listActivity': {
                'method': 'GET',
            },
            'listFollowers': {
                'method': 'GET',
            },
            'listFollowing': {
                'method': 'GET',
            },
            'listForums': {
                'method': 'GET',
            },
        },
        'whitelists': {
            'add': {
                'method': 'POST',
            },
            'list': {
                'method': 'GET',
            },
            'remove': {
                'method': 'POST',
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