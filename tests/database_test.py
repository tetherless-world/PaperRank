from context import PaperRank

import unittest


class TestDatabase(unittest.TestCase):
    """Tests for the 'database' module
    """

    def test_connectRedis(self):
        """Testing the Redis database connector, with connection specification
        from configuration.
        """
        PaperRank.util.configSetup()
        config = PaperRank.util.config
        test_db = PaperRank.util.Database(host=config.test['redis']['host'],
                                          port=config.test['redis']['port'], 
                                          db=config.test['redis']['db'])
        response = test_db.checkConnection()
        self.assertTrue(response)
