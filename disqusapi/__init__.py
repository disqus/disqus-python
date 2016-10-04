"""
disqus-python
~~~~~~~~~~~~~

disqus = DisqusAPI(api_secret=secret_key)
disqus.get('trends.listThreads')

"""
try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('disqusapi').version
except Exception:  # pragma: no cover
    __version__ = 'unknown'

import re
import zlib
import os.path
import warnings
import socket

try:
    import simplejson as json
except ImportError:
    import json

from disqusapi.paginator import Paginator
from disqusapi import compat
from disqusapi.compat import http_client as httplib
from disqusapi.compat import urllib_parse as urllib
from disqusapi.utils import build_interfaces_by_method

__all__ = ['DisqusAPI', 'Paginator']

with open(os.path.join(os.path.dirname(__file__), 'interfaces.json')) as fp:
    INTERFACES = json.load(fp)

HOST = 'disqus.com'

CHARSET_RE = re.compile(r'charset=(\S+)')
DEFAULT_ENCODING = 'utf-8'


class InterfaceNotDefined(NotImplementedError):
    pass


class InvalidHTTPMethod(TypeError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "expected 'GET' or 'POST', got: %r" % self.message


class FormattingError(ValueError):
    pass


class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)


class InvalidAccessToken(APIError):
    pass

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
    def __init__(self, api, interfaces=INTERFACES, node=None, tree=()):
        self.api = api
        self.node = node
        self.interfaces = interfaces
        if node:
            tree = tree + (node,)
        self.tree = tree
        self.interfaces_by_method = {}

    def update_interface(self, interface):
        raise NotImplemented

    def __getattr__(self, attr):
        if attr in getattr(self, '__dict__'):
            return getattr(self, attr)
        if attr == 'interface':
            raise InterfaceNotDefined('You must use ``update_interface`` now.')
        interface = {}
        try:
            interface = self.interfaces[attr]
        except KeyError:
            try:
                interface = self.interfaces_by_method[attr]
            except KeyError:
                pass
        return Resource(self.api, interface, attr, self.tree)

    def __call__(self, endpoint=None, **kwargs):
        return self._request(endpoint, **kwargs)

    def _request(self, endpoint=None, **kwargs):
        if endpoint is not None:
            # Handle undefined interfaces
            resource = self.interfaces.get(endpoint, {})
            endpoint = endpoint.replace('.', '/')
        else:
            resource = self.interfaces
            endpoint = '/'.join(self.tree)
        for k in resource.get('required', []):
            if k not in (x.split(':')[0] for x in compat.iterkeys(kwargs)):
                raise ValueError('Missing required argument: %s' % k)

        method = kwargs.pop('method', resource.get('method'))

        if not method:
            raise InterfaceNotDefined(
                'Interface is not defined, you must pass ``method`` (HTTP Method).')

        method = method.upper()
        if method not in ('GET', 'POST'):
            raise InvalidHTTPMethod(method)

        api = self.api

        version = kwargs.pop('version', api.version)
        format = kwargs.pop('format', api.format)
        formatter, formatter_error = api.formats[format]

        path = '/api/%s/%s.%s' % (version, endpoint, format)

        if 'api_secret' not in kwargs and api.secret_key:
            kwargs['api_secret'] = api.secret_key
        if 'api_public' not in kwargs and api.public_key:
            kwargs['api_key'] = api.public_key

        # We need to ensure this is a list so that
        # multiple values for a key work
        params = []
        for k, v in compat.iteritems(kwargs):
            if isinstance(v, (list, tuple)):
                for val in v:
                    params.append((k, val))
            else:
                params.append((k, v))

        headers = {
            'User-Agent': 'disqus-python/%s' % __version__,
            'Accept-Encoding': 'gzip',
        }

        if method == 'GET':
            path = '%s?%s' % (path, urllib.urlencode(params))
            data = ''
        else:
            data = urllib.urlencode(params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        conn = httplib.HTTPSConnection(HOST, timeout=api.timeout)
        conn.request(method, path, data, headers)
        response = conn.getresponse()

        try:
            body = response.read()
        finally:
            # Close connection
            conn.close()

        if response.getheader('Content-Encoding') == 'gzip':
            # See: http://stackoverflow.com/a/2424549
            body = zlib.decompress(body, 16 + zlib.MAX_WBITS)

        # Determine the encoding of the response and respect
        # the Content-Type header, but default back to utf-8
        content_type = response.getheader('Content-Type')
        if content_type is None:
            encoding = DEFAULT_ENCODING
        else:
            try:
                encoding = CHARSET_RE.search(content_type).group(1)
            except AttributeError:
                encoding = DEFAULT_ENCODING

        body = body.decode(encoding)

        try:
            # Coerce response to Python
            data = formatter(body)
        except formatter_error:
            raise FormattingError(body)

        if response.status != 200:
            raise ERROR_MAP.get(data['code'], APIError)(data['code'], data['response'])

        if isinstance(data['response'], list):
            return Result(data['response'], data.get('cursor'))
        return data['response']


class DisqusAPI(Resource):
    formats = {
        'json': (json.loads, ValueError),
    }

    def __init__(self, secret_key=None, public_key=None, format='json', version='3.0',
                 timeout=None, interfaces=INTERFACES, **kwargs):
        self.secret_key = secret_key
        self.public_key = public_key
        if not public_key:
            warnings.warn('You should pass ``public_key`` in addition to your secret key.')
        self.format = format
        self.version = version
        self.timeout = timeout or socket.getdefaulttimeout()
        self.interfaces = interfaces
        self.interfaces_by_method = build_interfaces_by_method(self.interfaces)
        super(DisqusAPI, self).__init__(self)

    @property
    def key(self):
        warnings.warn(
            "'key' is deprecated in favor of directly accessing the `secret_key` attribute",
            DeprecationWarning)
        return self.secret_key

    def setSecretKey(self, key):
        warnings.warn(
            "'setSecretKey' is deprecated in favor of directly setting the 'secret_key' attribute",
            DeprecationWarning)
        self.secret_key = key

    def setKey(self, key):
        warnings.warn(
            "'setKey' is deprecated in favor of directly setting the 'secret_key' attribute",
            DeprecationWarning)
        self.secret_key = key

    def setPublicKey(self, key):
        warnings.warn(
            "'setPublicKey' is deprecated in favor of directly setting the 'public_key' attribute",
            DeprecationWarning)
        self.public_key = key

    def setFormat(self, format):
        warnings.warn(
            "'setFormat' is deprecated in favor of directly setting the 'format' attribute",
            DeprecationWarning)
        self.format = format

    def setVersion(self, version):
        warnings.warn(
            "'setVersion' is deprecated in favor of directly setting the 'version' attribute",
            DeprecationWarning)
        self.version = version

    def setTimeout(self, timeout):
        warnings.warn(
            "'setTimeout' is deprecated in favor of directly setting the 'timeout' attribute",
            DeprecationWarning)
        self.timeout = timeout

    def update_interface(self, new_interface):
        self.interfaces.update(new_interface)
        self.interfaces_by_method = build_interfaces_by_method(self.interfaces)
