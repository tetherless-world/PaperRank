from context import PaperRank

import unittest


class TestDBConnector(unittest.TestCase):
    """Tests for the 'dbconnector' module
    """

    def test_connectRedis(self):
        """Testing the Redis database connector, with connection specification
        from configuration.
        """
        PaperRank.util.configSetup()
        config = PaperRank.util.config
        test_db = PaperRank.util.dbconnector.Redis()
        response = test_db.connect(host=config.redis['host'],
                                   port=config.redis['port'], db=0)
        self.assertTrue(response)
