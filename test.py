import unittest
import os
from api import *

api_key = os.environ.get('PG_API_KEY') or 'apikey-xxxxxxx'

class TestApi(unittest.TestCase):
    def test_invalid_token(self):
        with self.assertRaises(PGApiError):
            result = Player(api_key='123')

    def test_apikey_missing(self):
        with self.assertRaises(ValueError):
            result = Player()

    def test_player(self):
        result = Player(api_key=api_key)
        self.assertIn('pgid', result.data)
        result = Player(api_key=api_key)
        self.assertIn('pgid', result.data)
        self.assertEqual(result.data.get('cached'),True)

    def test_castleinfo(self):
        with self.assertRaises(ValueError):
            result = CastleInfo(api_key=api_key, cont_ids=[])
        with self.assertRaises(ValueError):
            result = CastleInfo(api_key=api_key, cont_ids=["abc"])
        result = CastleInfo(api_key=api_key, cont_ids=["1-A123-1"])
        self.assertIn("1-A123-1", result.data)

    def test_troopcount(self):
    	result = AtlasTroopCount(api_key=api_key)
    	self.assertIn("timestamp", result.data)
    	self.assertIn("troop_count", result.data)



if __name__ == '__main__':
    unittest.main()