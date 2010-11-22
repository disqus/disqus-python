import unittest

from disqusapi import DisqusAPI, APIError

class DisqusAPITest(unittest.TestCase):
    API_SECRET = 'b'*64

    def test_setSecretKey(self):
        api = DisqusAPI(api_secret='a')
        self.assertEquals(api.api_secret, 'a')
        api.setSecretKey('b')
        self.assertEquals(api.api_secret, 'b')
    
    def test_users_listActivity(self):
        api = DisqusAPI(self.API_SECRET)
        self.assertRaises(APIError, api.users.listActivity, foo='bar')

if __name__ == '__main__':
    unittest.main()