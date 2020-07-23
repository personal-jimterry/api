import unittest

from api import *

api_key = 'apikey-xxxxxxx'



class TestApi(unittest.TestCase):
    def test_apikey_missing(self):
    	with self.assertRaises(ValueError):
	        result = Player()

    def test_player(self):
        """
        Test player api
        """
        data = [1, 2, 3]
        result = Player(api_key=api_key)
        self.assertIn('pgid', result)


    def test_castleinfo(self):
        with self.assertRaises(ValueError):
            result = CastleInfo(api_key=api_key, cont_ids=[])
        with self.assertRaises(ValueError):
            result = CastleInfo(api_key=api_key, cont_ids=["abc"])
        with self.assertRaises(ValueError):
        	result = CastleInfo(api_key=api_key, cont_ids=["1-A123-1"])

if __name__ == '__main__':
    unittest.main()