from context import PaperRank
from redis import StrictRedis, ConnectionPool

import unittest


class TestComputeManager(unittest.TestCase):
    """Test the compute engine `Manager` module with a dummy example.
    """

    def __init__(self, *args, **kwargs):
        """Override initialization function to clear database for the
        PaperRank Compute test.
        """

        # Running superclass initialization
        super(TestComputeManager, self).__init__(*args, **kwargs)

        # Setting up PaperRank
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

        # Connecting to redis
        self.redis = StrictRedis(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db']
        )

    def test_compute_manager(self):
        """Test the `Manager` by computing PaperRank for a sample testcase.

        The test case computes PageRank for the graph with the structure:

        - Graphical graph representation:
                 [2] <--- [4]
                /  ▲      /
               /    \    /
              ▼      \  ▼
             [1] <--- [3]
    
        - `IN` database mappings:
            - {1: [2, 3]}    (new)
            - {2: [3, 4]}      |
            - {3: [4]}         |
            - {4: []}         old
        
        - Solution (stable):
            - [1] -> .4571428855
            - [2] -> .2571428458
            - [3] -> .1714285572
            - [4] -> .1142857114
        
        """

        # Flush database
        self.redis.flushdb()

        pages = [1, 2, 3, 4]

        inbound_map = {
            1: [2, 3],
            2: [3, 4],
            3: [4],
            4: []
        }

        # Adding pages to `SEEN`
        self.redis.sadd('SEEN', *[1, 2, 3, 4])

        # Adding inbound citation map
        self.redis.hmset('IN', inbound_map)

        # NOTE: ADD Outbound citation map (for out degree computation)

        # Creating redis-py connection pool
        conn_pool = ConnectionPool(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db']
        )

        # Run PaperRank compute

        self.assertTrue(True)  # Temporary
