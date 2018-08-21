from context import PaperRank

import numpy as np

import unittest


class TestTrustKMeans(unittest.TestCase):
    """Tests for the `model` module in the Trust engine.
    """

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestTrustKMeans, self).__init__(*args, **kwargs)

        # Setting up PaperRank
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

    def test_clustering(self):
        """Function to test the `computeKMeansProportions` function in the
        trust engine.
        """

        # Test data setup
        test_data = np.array([1, 5, 8, 10, 15, 45, 52, 55, 95, 102])

        # Expected proportions for 3 clusters
        real_props = np.array([.5, .3, .2])

        # Computing candidate proportions using the trust engine
        candidate_props = PaperRank.trust.model.computeKMeansProportions(
                                                    data=test_data,
                                                    n_clusters=3)

        self.assertListEqual(list(candidate_props), list(real_props))
