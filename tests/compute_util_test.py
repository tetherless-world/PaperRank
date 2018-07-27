from context import PaperRank
from redis import StrictRedis
import numpy as np

import unittest


class TestComputeUtil(unittest.TestCase):
    """Test the compute engine `util` module.
    """

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestComputeUtil, self).__init__(*args, **kwargs)

        # Setting up PaperRank
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

        # Connecting to redis
        self.redis = StrictRedis(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db']
        )

    def test_buildOutDegreeMap(self):
        """Test the `buildOutDegreeMap` function from the `util` submodule.
        This function also tests the behavior of only computing out degrees
        for IDs that do not yet have them computed.
        """

        # Flush db, set up example data
        self.redis.flushdb()

        # Setting up sample data
        outbound_map = {
            1: [2, 3],
            2: [3, 4],
            3: [4],
            4: [],
            5: [1, 2, 3, 4]
        }

        # Expected output
        expected_out_degree = {
            b'1': b'2',
            b'2': b'2',
            b'3': b'1',
            b'4': b'0',
            b'5': b'42'
        }

        # Adding outbound citation map, and dummy #5 citation
        self.redis.hmset('OUT', outbound_map)
        self.redis.hmset('OUT_DEGREE', {5: 42})

        # Running util function
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        # Checking output
        out_degree = self.redis.hgetall('OUT_DEGREE')

        self.assertDictEqual(out_degree, expected_out_degree)

    def test_constructStochasticMatrix(self):
        """Test the functionality of the `constructStochasticMatrix` method.
        """

        # Setup test
        id_list = self.dataSetup()

        m = PaperRank.compute.stochastic_matrix.constructStochasticMatrix(
            r=self.redis,
            seen=id_list
        )

        m_expected = np.matrix('0 1 .5 0; 0 0 .5 .5; 0 0 0 .5; 0 0 0 0',
                               dtype=np.float32)

        self.assertEqual(str(m.todense()), str(m_expected))

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
        self.old_scores = {
            2: .5,
            3: .25,
            4: .25
        }
        self.redis.hmset('PaperRank', self.old_scores)

        # Running util to set up out degree map
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        return np.array([1, 2, 3, 4], dtype=np.int)
