from context import PaperRank

import unittest


class TestDatabase(unittest.TestCase):
    """Tests for the 'database' module
    """

    def __init__(self, *args, **kwargs):
        super(TestDatabase, self).__init__(*args, **kwargs)
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config
        self.db = PaperRank.util.Database(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db'])

    def test_connectRedis(self):
        """Redis database connector connection test.
        """

        response = self.db.checkConnection()
        self.assertTrue(response)

    def test_addMultiple(self):
        """`addMultiple` function test.
        """

        # Adding list of numbers to 'seen' test database (a Set)
        setAdd = self.db.addMultiple(database='S',
                                     data=[1, 2, 3, 4, 5])
        # Add multiple entry dict to 'out' test database (a HashMap)
        hashmapAdd = self.db.addMultiple(database='O',
                                         data={'first': 'rukmal',
                                               'last': 'weerawarana'})
        # Both are successful
        self.assertTrue(setAdd and hashmapAdd)

    def test_removeMultiple(self):
        """`removeMultiple` function test.
        """

        # Add some elements to Set
        self.db.addMultiple(database='S', data=[1, 2, 34, 5])
        # Removing elements
        setRemove = self.db.removeMultiple(database='S', data=[2, 34])

        # Add some elements to HashMap
        self.db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana',
                                  'age': '22',
                                  'location': 'Troy, NY'})
        # Removing elements
        hashmapRemove = self.db.removeMultiple(database='O',
                                               data=['first', 'age'])

        # Both are successful
        self.assertTrue(setRemove and hashmapRemove)

    def test_contains(self):
        """`contains` function test.
        """

        # Add items to Set
        self.db.addMultiple(database='S', data=[1, 2, 3, 4, 5])
        setContains = self.db.contains(database='S', key='1')

        # Add items to HashMap
        self.db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana'})
        # Checking  elements
        hashmapContains = self.db.contains(database='O',
                                           key='first')

        self.assertTrue(setContains and hashmapContains)

    def test_pop(self):
        """`pop` function test.
        """

        # Add items to Set
        self.db.addMultiple(database='S', data=[1, 2, 3, 4, 5])

        # Pop 2 elements
        popped = self.db.pop(database='S', n=2)

        # pop was successful
        self.assertEqual(len(popped), 2)

    def test_size(self):
        """`size` function test.
        """

        # Flush test database (manual access)
        self.db.r.flushdb()

        # Add items to Set
        self.db.addMultiple(database='S', data=[1, 2])
        # Getting size
        setSize = self.db.size(database='S')

        # Add items to HashMap
        self.db.addMultiple(database='O',
                            data={'first': 'rukmal',
                                  'last': 'weerawarana'})
        # Getting size
        hashmapSize = self.db.size(database='O')

        # size was sucessful
        self.assertEqual(setSize + hashmapSize, 4)
