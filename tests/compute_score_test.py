from context import PaperRank
from redis import StrictRedis
import numpy as np

import unittest


class TestComputeScore(unittest.TestCase):
    """Test the compute engine 'score' module.
    """

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestComputeScore, self).__init__(*args, **kwargs)

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

        return np.array([1, 2, 3, 4], dtype=str)

    def test_computeIterationScore(self):
        """Test the `computeIterationScore` function from the `score` submodule.
        """

        # Setting up test environment
        id_list = self.dataSetup()

        # Running iteration compute function
        scores = PaperRank.compute.score.computeIterationScore(
            r=self.redis, id_list=id_list)
        
        # Test verification
        # (Computing score manually)

        out_degree = {
            1: 0,
            2: 1,
            3: 2,
            4: 2
        }

        def manual_compute():
            beta = self.config.compute['beta']
            expected_scores = []
            id_list = [1, 2, 3, 4]
            for paper_id in id_list:
                score = 0
                inbound_list = self.inbound_map[paper_id]

                for inbound in inbound_list:
                    score += self.old_scores[inbound] \
                        / out_degree[inbound] * beta

                expected_scores.append(score)
            leaked_pr = 1 - sum(expected_scores)

            n = len(expected_scores)
            expected_scores = [s + (leaked_pr / n) for s in expected_scores]
            return expected_scores
        
        expected_scores = manual_compute()

        self.assertListEqual(list(scores), expected_scores)

    def test_computeStableScore(self):
        """Test the `calculate` function from the `score` submodule.
        """

        # Setting up the test environment
        id_list = self.dataSetup()

        # Running stable compute function
        PaperRank.compute.score.calculate(r=self.redis, id_list=id_list)

        # Ensuring probability distribution by checking if sum is 1
        scores_raw = self.redis.hgetall('PaperRank')
        scores = np.array([], dtype=float)
        for k, v in scores_raw.items():
            scores = np.append(scores, v)
        scores = np.array(scores).astype(np.float)

        self.assertEqual(np.sum(scores), 1.0)
