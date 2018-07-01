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
        """Redis database connector connection test.
        """

        test_db = self.__setup()
        response = test_db.checkConnection()
        self.assertTrue(response)

    def test_addMultiple(self):
        """`addMultiple` function test.
        """
        
        test_db = self.__setup()

        # Adding list of numbers to 'seen' test database (a Set)
        setAdd = test_db.addMultiple(database='S',
                                     data=[1, 2, 3, 4, 5])
        # Add multiple entry dict to 'out' test database (a HashMap)
        hashmapAdd = test_db.addMultiple(database='O',
                                         data={'first': 'rukmal',
                                               'last': 'weerawarana'})
        # Both are successful
        self.assertTrue(setAdd and hashmapAdd)

    def test_removeMultiple(self):
        """`removeMultiple` function test.
        """

        test_db = self.__setup()

        # Add some elements to Set
        test_db.addMultiple(database='S', data=[1, 2, 34, 5])
        # Removing elements
        setRemove = test_db.removeMultiple(database='S', data=[2, 34])

        # Add some elements to HashMap
        test_db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana',
                                  'age': '22',
                                  'location': 'Troy, NY'})
        # Removing elements
        hashmapRemove = test_db.removeMultiple(database='O',
                                               data=['first', 'age'])

        # Both are successful
        self.assertTrue(setRemove and hashmapRemove)

    def test_contains(self):
        """`contains` function test.
        """

        test_db = self.__setup()

        # Add items to Set
        test_db.addMultiple(database='S', data=[1, 2, 3, 4, 5])
        setContains = test_db.contains(database='S', key='1')

        # Add items to HashMap
        test_db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana'})
        # Checking  elements
        hashmapContains = test_db.contains(database='O',
                                           key='first')

        self.assertTrue(setContains and hashmapContains)

    def test_pop(self):
        """`pop` function test.
        """

        test_db = self.__setup()

        # Add items to Set
        test_db.addMultiple(database='S', data=[1, 2, 3, 4, 5])

        # Pop 2 elements
        popped = test_db.pop(database='S', n=2)
        print(popped)
        # pop was successful
        self.assertEqual(len(popped), 2)

    def test_size(self):
        """`size` function test.
        """

        test_db = self.__setup()

        # Add items to Set
        test_db.addMultiple(database='S', data=[1, 2])
        # Getting size
        setSize = test_db.size(database='S')

        # Add items to HashMap
        test_db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana'})
        # Getting size
        hashmapSize = test_db.size(database='O')

        # size was sucessful
        self.assertEqual(setSize + hashmapSize, 4)
