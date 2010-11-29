import unittest

from disqusapi import DisqusAPI, APIError

class DisqusAPITest(unittest.TestCase):
    API_SECRET = 'b'*64

    def test_setKey(self):
        api = DisqusAPI('a')
        self.assertEquals(api.key, 'a')
        api.setKey('b')
        self.assertEquals(api.key, 'b')

    def test_setFormat(self):
        api = DisqusAPI()
        self.assertEquals(api.format, 'json')
        api.setFormat('jsonp')
        self.assertEquals(api.format, 'jsonp')
    
    def test_setVersion(self):
        api = DisqusAPI()
        self.assertEquals(api.version, '3.0')
        api.setVersion('3.1')
        self.assertEquals(api.version, '3.1')
    
    def test_users_listActivity(self):
        api = DisqusAPI(self.API_SECRET)
        self.assertRaises(APIError, api.users.listActivity, foo='bar')

if __name__ == '__main__':
    unittest.main()