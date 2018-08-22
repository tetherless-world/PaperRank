from context import PaperRank

import numpy as np

import unittest


class TestGammaMix(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestGammaMix, self).__init__(*args, **kwargs)

        # Setting up PaperRank
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

        # Isolating gamma_mix
        self.gamma_mix = PaperRank.trust.model.gamma_mix

    def test_shiftData(self):
        """Test the functionality of the `shiftData` function in the
        util module.
        """

        # Setting up test data
        test_data = np.array([-5, -4, -3, -2])

        # Manually shifting with correct formula
        expected_shifted = test_data + np.absolute(np.min(test_data)) \
            + self.config.trust['gamma_shift_constant']

        # Computing candidate shifted data
        candidate_shifted = self.gamma_mix.util.shiftData(data=test_data)

        self.assertListEqual(list(expected_shifted), list(candidate_shifted))
