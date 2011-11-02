import mock
import os
import unittest

import disqusapi
from disqusapi.utils import get_mac_signature

def requires(*env_vars):
    def wrapped(func):
        for k in env_vars:
            if not os.environ.get(k):
                return
        return func
    return wrapped

class MockResponse(object):
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def read(self):
        return self.body

class DisqusAPITest(unittest.TestCase):
    API_SECRET = 'b'*64
    API_PUBLIC = 'c'*64
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

    def test_paginator(self):
        def iter_results():
            for n in xrange(11):
                yield disqusapi.Result(
                    response=[n]*10,
                    cursor={
                        'id': n,
                        'more': n < 10,
                    },
                )

        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)

        with mock.patch('disqusapi.Resource._request') as _request:
            iterator = iter_results()
            _request.return_value = iterator.next()
            paginator = disqusapi.Paginator(api.posts.list, forum='disqus')
            n = 0
            for n, result in enumerate(paginator(limit=100)):
                if n % 10 == 0:
                    iterator.next()
        self.assertEquals(n, 99)

    def test_signed_request(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)

        with mock.patch('httplib.HTTPConnection.request') as request:
            with mock.patch('httplib.HTTPConnection.getresponse') as getresponse:
                getresponse.return_value = MockResponse('''{
                    "response": {}
                }''', status=200)
                api.posts.list(forum='disqus')

            args, kwargs = request.call_args
        self.assertEquals(args[0], 'GET')
        self.assertEquals(args[1], '/api/3.0/posts/list.json?forum=disqus')
        body = args[2].split('\n')
        self.assertEquals(len(body), 8) # 6 parts to a signed body
        timestamp, nonce = body[0].split(':')
        self.assertTrue(len(nonce) <= 32)
        self.assertEquals(body[1], 'GET')
        self.assertEquals(body[2], '/api/3.0/posts/list.json')
        self.assertEquals(body[3], 'disqus.com')
        self.assertEquals(body[4], '80')
        self.assertEquals(body[5], 'ytsXfVhvWMMkPyBsMPkn6DYXRqc=')
        self.assertEquals(body[6], '') # ext
        self.assertEquals(body[7], '') # always empty
        headers = args[3]
        signature = get_mac_signature(self.API_SECRET, args[2])
        self.assertTrue('Authorization' in headers)
        auth_header = 'MAC id="%s", nonce="%s:%s", body-hash="ytsXfVhvWMMkPyBsMPkn6DYXRqc=", mac="%s"' % (
            self.API_PUBLIC,
            timestamp,
            nonce,
            signature,
        )
        self.assertEquals(headers['Authorization'], auth_header)

    def test_signed_request_with_access_token(self):
        api = disqusapi.DisqusAPI(self.API_SECRET, self.API_PUBLIC)

        with mock.patch('httplib.HTTPConnection.request') as request:
            with mock.patch('httplib.HTTPConnection.getresponse') as getresponse:
                getresponse.return_value = MockResponse('''{
                    "response": {}
                }''', status=200)
                api.posts.list(forum='disqus', access_token='z'*64)

            args, kwargs = request.call_args
        self.assertEquals(args[0], 'GET')
        self.assertEquals(args[1], '/api/3.0/posts/list.json?access_token=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&forum=disqus')
        body = args[2].split('\n')
        self.assertEquals(len(body), 8) # 6 parts to a signed body
        timestamp, nonce = body[0].split(':')
        self.assertTrue(len(nonce) <= 32)
        self.assertEquals(body[1], 'GET')
        self.assertEquals(body[2], '/api/3.0/posts/list.json')
        self.assertEquals(body[3], 'disqus.com')
        self.assertEquals(body[4], '80')
        self.assertEquals(body[5], 'vfI2fQSNV+WQvdBFwiB1BJvMcBw=')
        self.assertEquals(body[6], '') # ext
        self.assertEquals(body[7], '') # always empty
        headers = args[3]
        signature = get_mac_signature(self.API_SECRET, args[2])
        self.assertTrue('Authorization' in headers)
        auth_header = 'MAC id="%s", nonce="%s:%s", body-hash="vfI2fQSNV+WQvdBFwiB1BJvMcBw=", mac="%s", access_token="%s"' % (
            self.API_PUBLIC,
            timestamp,
            nonce,
            signature,
            'z'*64,
        )
        self.assertEquals(headers['Authorization'], auth_header)

if __name__ == '__main__':
    unittest.main()