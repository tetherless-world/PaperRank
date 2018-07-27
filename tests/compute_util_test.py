from context import PaperRank
from redis import StrictRedis

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

        # Flush db, set up example data
        self.redis.flushdb()
    
    def test_buildOutDegreeMap(self):
        """Test the `buildOutDegreeMap` function from the `util` submodule.
        """

        # Setting up sample data
        outbound_map = {
            1: [2, 3],
            2: [3, 4],
            3: [4],
            4: []
        }

        # Expected output
        expected_out_degree = {
            b'1': b'2',
            b'2': b'2',
            b'3': b'1',
            b'4': b'0'
        }

        # Adding outbound citation map
        self.redis.hmset('OUT', outbound_map)

        # Running util function
        PaperRank.compute.util.buildOutDegreeMap(r=self.redis)

        # Checking output
        out_degree = self.redis.hgetall('OUT_DEGREE')

        self.assertDictEqual(out_degree, expected_out_degree)
