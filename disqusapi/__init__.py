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
import time
import urllib
import uuid
import warnings

from disqusapi.paginator import Paginator
from disqusapi.utils import (get_normalized_params,
                             get_normalized_request_string, get_mac_signature,
                             get_body_hash)

__all__ = ['DisqusAPI', 'Paginator']

INTERFACES = simplejson.loads(open(os.path.join(os.path.dirname(__file__), 'interfaces.json'), 'r').read())

HOST = 'disqus.com'
SSL_HOST = HOST

class InterfaceNotDefined(NotImplementedError): pass
class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

class InvalidAccessToken(APIError): pass

ERROR_MAP = {
    18: InvalidAccessToken,
}

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
            interface[attr] = {}
            # raise InterfaceNotDefined(attr)
        return Resource(self.api, interface[attr], attr, self.tree)

    def __call__(self, **kwargs):
        return self._request(**kwargs)

    def _request(self, **kwargs):
        # Handle undefined interfaces
        resource = self.interface
        for k in resource.get('required', []):
            if k not in [ x.split(':')[0] for x in kwargs.keys() ]:
                raise ValueError('Missing required argument: %s' % k)

        method = kwargs.get('method', resource.get('method'))

        if not method:
            raise InterfaceNotDefined('Interface is not defined, you must pass ``method`` (HTTP Method).')

        api = self.api

        version = kwargs.pop('version', api.version)
        format = kwargs.pop('format', api.format)

        if api.is_secure:
            host = 'https://%s' % SSL_HOST
            conn = httplib.HTTPSConnection(SSL_HOST)
        else:
            host = 'http://%s' % HOST
            conn = httplib.HTTPConnection(HOST)

        path = '/api/%s/%s.%s' % (version, '/'.join(self.tree), format)
        url = '%s%s' % (host, path)

        # We need to ensure this is a list so that
        # multiple values for a key work
        params = []
        for k, v in kwargs.iteritems():
            if isinstance(v, (list, tuple)):
                for val in v:
                    params.append((k, val))
            else:
                params.append((k, v))

        if method == 'GET':
            path = '%s?%s' % (path, get_normalized_params(params))

        headers = {
            'User-Agent': 'disqus-python/%s' % __version__
        }

        public_key = kwargs.pop('public_key', api.public_key)

        if public_key:
            # If we have both public and secret keys we can safely sign the request
            # (which also happens to enable oauth access tokens)
            nonce = '%s:%s' % (time.time(), uuid.uuid4().hex)
            body_hash = get_body_hash(params)
            data = get_normalized_request_string(method, url, nonce, params, body_hash=body_hash)
            signature = get_mac_signature(kwargs.pop('secret_key', api.secret_key), data)
            auth_params = [
                ('id', public_key),
                ('nonce', nonce),
                ('body-hash', body_hash),
                ('mac', signature),
            ]
            access_token = kwargs.pop('access_token', None)
            if access_token:
                auth_params.append(('access_token', access_token))
            headers['Authorization'] = 'MAC %s' % ', '.join('%s="%s"' % (k, v) for k, v in auth_params)
        else:
            if 'api_secret' not in kwargs:
                kwargs['api_secret'] = api.secret_key

            if method == 'GET':
                data = ''
            else:
                data = urllib.urlencode(data)

        conn.request(method, path, data, headers)

        response = conn.getresponse()
        # Let's coerce it to Python
        data = api.formats[format](response.read())

        if response.status != 200:
            raise ERROR_MAP.get(data['code'], APIError)(data['code'], data['response'])

        if isinstance(data['response'], list):
            return Result(data['response'], data.get('cursor'))
        return data['response']

class DisqusAPI(Resource):
    formats = {
        'json': lambda x: simplejson.loads(x),
    }

    def __init__(self, secret_key=None, public_key=None, format='json', version='3.0', is_secure=False):
        self.secret_key = secret_key
        self.public_key = public_key
        if not public_key:
            warnings.warn('You should use ``public_key`` in addition to your secret key for signing requests.')
        self.format = format
        self.version = version
        self.is_secure = is_secure
        super(DisqusAPI, self).__init__(self)

    def _request(self, **kwargs):
        raise SyntaxError('You cannot call the API without a resource.')

    def _get_key(self):
        return self.secret_key
    key = property(_get_key)

    def setSecretKey(self, key):
        self.secret_key = key
    setKey = setSecretKey

    def setPublicKey(self, key):
        self.public_key = key

    def setFormat(self, format):
        self.format = format

    def setVersion(self, version):
        self.version = version
