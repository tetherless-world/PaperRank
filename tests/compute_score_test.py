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

        # Flush db, set up example data
        self.redis.flushdb()

    def test_computeIterationScore(self):
        """Test the `computeIterationScore` function from the `score` submodule.

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
            - {1: (this is what we compute)}
            - {2: .5}
            - {3: .25}
            - {4: .25}
        
        - Expected solution
            - {1: } (figure this out)
        """

        # Setting up sample data
        inbound_map = {
            1: [2, 3],
            2: [3, 4],
            3: [4],
            4: []
        }
        self.redis.hmset('IN', inbound_map)
        outbound_map = {
            1: [],
            2: [1],
            3: [1, 2],
            4: [2, 3]
        }
        self.redis.hmset('OUT', outbound_map)
        old_scores = {
            2: .5,
            3: .25,
            4: .25
        }
        self.redis.hmset('PaperRank', old_scores)
        out_degree = {
            1: 0,
            2: 1,
            3: 2,
            4: 2
        }
        id_list = np.array([1, 2, 3, 4], dtype=str)

        # Running util to set up out degree map
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        # Running iteration compute function
        scores = PaperRank.compute.score.computeIterationScore(
            r=self.redis, id_list=id_list)
        
        # Test verification
        # (Computing score manually)

        def manual_compute():
            beta = self.config.compute['beta']
            expected_scores = []
            id_list = [1, 2, 3, 4]
            for paper_id in id_list:
                score = 0
                inbound_list = inbound_map[paper_id]

                for inbound in inbound_list:
                    score += old_scores[inbound] / out_degree[inbound] * beta

                expected_scores.append(score)
            leaked_pr = 1 - sum(expected_scores)

            n = len(expected_scores)
            expected_scores = [s + (leaked_pr / n) for s in expected_scores]
            return expected_scores
        
        expected_scores = manual_compute()

        self.assertListEqual(list(scores), expected_scores)
