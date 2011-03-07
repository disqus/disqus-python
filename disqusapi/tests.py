import os
import unittest

import disqusapi

def requires(*env_vars):
    def wrapped(func):
        for k in env_vars:
            if not os.environ.get(k):
                return
        return func
    return wrapped

class DisqusAPITest(unittest.TestCase):
    DUMMY_API_SECRET = 'b'*64
    API_SECRET = os.environ.get('DISQUS_API_SECRET')
    HOST = os.environ.get('DISQUS_API_HOST', disqusapi.HOST)
    
    def setUp(self):
        disqusapi.HOST = self.HOST
    
    def test_setKey(self):
        api = disqusapi.DisqusAPI('a')
        self.assertEquals(api.key, 'a')
        api.setKey('b')
        self.assertEquals(api.key, 'b')

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
    
    def test_users_listActivity(self):
        api = disqusapi.DisqusAPI(self.DUMMY_API_SECRET)
        self.assertRaises(disqusapi.APIError, api.users.listActivity, foo='bar')

    @requires('DISQUS_API_SECRET')
    def test_paginator(self):
        api = disqusapi.DisqusAPI(self.API_SECRET)
        paginator = disqusapi.Paginator(api.posts.list, forum='disqus')
        results = list(paginator(limit=100))
        self.assertEquals(len(results), 100)

if __name__ == '__main__':
    unittest.main()