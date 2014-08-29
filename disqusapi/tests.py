import mock
import os
import socket
import unittest

import disqusapi
from disqusapi.compat import xrange

extra_interface = {
    "reserved": {
        "global": {
            "word": {
                "method": "GET",
                "required": [
                    "text",
                ],
                "formats": [
                    "json",
                ],
            }
        }
    }
}


extra_interface = {
    "reserved": {
        "global": {
            "word": {
                "method": "GET",
                "required": [
                    "text",
                ],
                "formats": [
                    "json",
                ],
            }
        }
    }
}


def requires(*env_vars):
    def wrapped(func):
        for k in env_vars:
            if not os.environ.get(k):
                return
        return func
    return wrapped


def iter_results():
    for n in xrange(11):
        yield disqusapi.Result(
            response=[n] * 10,
            cursor={
                'id': n,
                'more': n < 10,
            },
        )


class MockResponse(object):
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def read(self):
        return self.body


class DisqusAPITest(unittest.TestCase):
    API_SECRET = 'b' * 64
    API_PUBLIC = 'c' * 64
    HOST = os.environ.get('DISQUS_API_HOST', disqusapi.HOST)

    def setUp(self):
        disqusapi.HOST = self.HOST

    def test_setKey(self):
        api = disqusapi.DisqusAPI('a', 'c')
        self.assertEquals(api.secret_key, 'a')
        api.setKey('b')
        self.assertEquals(api.secret_key, 'b')

    def test_setSecretKey(self):
        api = disqusapi.DisqusAPI('a', 'c')
        self.assertEquals(api.secret_key, 'a')
        api.setSecretKey('b')
        self.assertEquals(api.secret_key, 'b')

    def test_setPublicKey(self):
        api = disqusapi.DisqusAPI('a', 'c')
        self.assertEquals(api.public_key, 'c')
        api.setPublicKey('b')
        self.assertEquals(api.public_key, 'b')

    def test_setFormat(self):
        api = disqusapi.DisqusAPI()
        self.assertEquals(api.format, 'json')
        api.setFormat('jsonp')
        self.assertEquals(api.format, 'jsonp')

    def test_setVersion(self):
        api = disqusapi.DisqusAPI()
        self.assertEquals(api.version, '3.0')
        api.setVersion('3.1')
        self.assertEquals(api.version, '3.1')

    def test_setTimeout(self):
        api = disqusapi.DisqusAPI()
        self.assertEquals(api.timeout, socket.getdefaulttimeout())
        api = disqusapi.DisqusAPI(timeout=30)
        self.assertEquals(api.timeout, 30)
        api.setTimeout(60)
        self.assertEquals(api.timeout, 60)

    def test_paginator(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)
        with mock.patch('disqusapi.Resource._request') as _request:
            iterator = iter_results()
            _request.return_value = next(iterator)
            paginator = disqusapi.Paginator(api, 'posts.list', forum='disqus')
            n = 0
            for n, result in enumerate(paginator(limit=100)):
                if n % 10 == 0:
                    next(iterator)
        self.assertEquals(n, 99)

    def test_paginator_legacy(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)
        with mock.patch('disqusapi.Resource._request') as _request:
            iterator = iter_results()
            _request.return_value = next(iterator)
            paginator = disqusapi.Paginator(api.posts.list, forum='disqus')
            n = 0
            for n, result in enumerate(paginator(limit=100)):
                if n % 10 == 0:
                    next(iterator)
        self.assertEquals(n, 99)

    def test_endpoint(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)
        with mock.patch('disqusapi.Resource._request') as _request:
            iterator = iter_results()
            _request.return_value = next(iterator)
            response1 = api.posts.list(forum='disqus')

        with mock.patch('disqusapi.Resource._request') as _request:
            iterator = iter_results()
            _request.return_value = next(iterator)
            response2 = api.get('posts.list', forum='disqus')

        self.assertEquals(len(response1), len(response2))

    def test_update_interface_legacy(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)
        try:
            with self.assertRaises(disqusapi.InterfaceNotDefined):
                api.interface.update(extra_interface)
        except TypeError:
            # remove when 2.6 is obsolete
            try:
                api.interface.update(extra_interface)
            except disqusapi.InterfaceNotDefined:
                pass
            else:
                raise unittest.failureException(
                    '%s not raised' % (str(disqusapi.InterfaceNotDefined)))

    def test_update_interface(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)
        api.update_interface(extra_interface)

if __name__ == '__main__':
    unittest.main()
