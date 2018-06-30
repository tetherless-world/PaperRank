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
        test_db = PaperRank.util.Database(host=config.redis['host'],
                                          port=config.redis['port'], 
                                          db=0)
        response = test_db.checkConnection()
        self.assertTrue(response)
