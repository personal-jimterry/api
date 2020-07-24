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

    def test_castles_metadata(self):
        result = CastleMetadata(api_key=api_key)
        self.assertIn("castles", result.data)

    def test_atlas_contribution(self):
        result = AtlasContribution(api_key=api_key)
        for player in result.data['entries']:
            self.assertEqual(hasattr(result, player['for_name']), True)

    def test_atlasTeamsMetadata(self):
        result = AtlasTeamsMetadata(api_key=api_key)
        self.assertIn("teams", result.data)

    def test_AtlasTeam(self):
        with self.assertRaises(PGApiError):
            result = AtlasTeam(api_key=api_key)
        result = AtlasTeam(api_key=api_key, team_name='DREADNOUGHT')
        self.assertIn("power_rank", result.data)

    def test_AtlasBattles(self):
        result = AtlasBattles(api_key=api_key)
        self.assertIn('cursor', result.data)
        result = AtlasBattles(api_key=api_key, cursor=result.data.get('cursor'))
        self.assertIn('cursor', result.data)

    def test_AtlasMonthlyKills(self):
        result = AtlasMonthlyKills(api_key=api_key, teams=['DREADNOUGHT', 'EquiIibrium'])
        self.assertIn("EquiIibrium", result.data)
        self.assertIn("DREADNOUGHT", result.data)

    def test_troopcount(self):
    	result = AtlasTroopCount(api_key=api_key)
    	self.assertIn("timestamp", result.data)
    	self.assertIn("troop_count", result.data)

    def test_AtlasAlliance(self):
        result = AtlasAlliance(api_key=api_key)
        self.assertIn('alliances', result.data)

    def test_AtlasEventScore(self):
        result = AtlasEventScore(api_key=api_key)
        self.assertIn("data", result.data)
        self.assertIn("team_name", result.data.get('data')[0])

if __name__ == '__main__':
    unittest.main()