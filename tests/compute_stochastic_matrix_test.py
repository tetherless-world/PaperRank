from context import PaperRank
from redis import StrictRedis
import numpy as np

import unittest


class TestComputeStochasticMatrix(unittest.TestCase):
    """Test the compute engine `stochastic_matrix` module.
    """

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestComputeStochasticMatrix, self).__init__(*args, **kwargs)

        # Setting up PaperRank
        PaperRank.util.configSetup()
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
        self.old_scores = {
            2: .5,
            3: .25,
            4: .25
        }
        self.redis.hmset('PaperRank', self.old_scores)

        # Running util to set up out degree map
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        return np.array([1, 2, 3, 4], dtype=np.int)

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
