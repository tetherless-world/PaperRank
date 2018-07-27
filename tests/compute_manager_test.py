from context import PaperRank

from redis import StrictRedis, ConnectionPool
import numpy as np

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
        PaperRank.util.configSetup(override='test.json')
        self.config = PaperRank.util.config

        # Connecting to redis
        self.redis = StrictRedis(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db']
        )

    def dataSetup(self) -> np.array:
        """Function to setup the test case described below.
        
            The test case is the following sample citation graph:

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
                - {4: []}        (old)
            
            - `OUT` database mappings:
                - {1: []}
                - {2: [1]}
                - {3: [1, 2]}
                - {4: [2, 3]}
            
            - Artificial PaperRanks (inserted)
                - {2: .5}
                - {3: .25}
                - {4: .25}


        Returns:
            np.array -- Array of IDs.
        """

        # Flush db
        self.redis.flushdb()

        # Setting up sample data
        self.inbound_map = {
            1: [2, 3],
            2: [3, 4],
            3: [4],
            4: []
        }
        self.redis.hmset('IN', self.inbound_map)
        outbound_map = {
            1: [],
            2: [1],
            3: [1, 2],
            4: [2, 3]
        }
        self.redis.hmset('OUT', outbound_map)
        seen = [1, 2, 3, 4]
        self.redis.sadd('SEEN', *seen)

        # Running util to set up out degree map
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        return np.array([1, 2, 3, 4], dtype=str)

    def test_compute_manager(self):
        """Test the `Manager` by computing PaperRank for a sample testcase.
        """

        # Setting up test environment
        id_list = self.dataSetup()
        # Reducing id_limit for test
        self.config.compute['id_limit'] = 10
        # Run PaperRank compute
        compute_manager = PaperRank.compute.Manager(r=self.redis)
        paperrank = compute_manager.start()

        self.assertEqual(len(paperrank), 4)
