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
