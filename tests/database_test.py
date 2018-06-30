from context import PaperRank

import unittest


class TestDatabase(unittest.TestCase):
    """Tests for the 'database' module
    """

    def __setup(self) -> PaperRank.util.Database:
        PaperRank.util.configSetup()
        config = PaperRank.util.config
        test_db = PaperRank.util.Database(host=config.test['redis']['host'],
                                          port=config.test['redis']['port'], 
                                          db=config.test['redis']['db'])
        test_db.r.flushdb()  # Accessing directly to flush testing database
        return test_db

    def test_connectRedis(self):
        """Testing the Redis database connector, with connection specification
        from configuration.
        """

        test_db = self.__setup()
        response = test_db.checkConnection()
        self.assertTrue(response)

    def test_setAddMultiple(self):
        """Testing the Redis `addMultiple` function for a Set.
        """
        test_db = self.__setup()
        # Adding list of numbers to 'seen' test database
        self.assertTrue(test_db.addMultiple(database='S',
                                            data=[1, 2, 3, 4, 5]))

    def test_hashmapAddMultiple(self):
        """Testing the Redis 'addMultiple' function for a HashMap.
        """
        test_db = self.__setup()
        self.assertTrue(test_db.addMultiple(database='O',
                                            data={'first': 'rukmal',
                                                  'last': 'weerawarana'}))
