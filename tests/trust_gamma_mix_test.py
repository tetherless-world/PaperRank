from context import PaperRank

from scipy.stats import gamma
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

    def test_gammaMixModel_posterior(self):
        """Test the functionality of the `computePosterior` function in the
        GammaMixModel module.
        """

        # Setting up test data and parameters
        test_data = np.array([1., 1., 1., 2., 1.5, 3, 1.1, 1.2])
        test_params = np.array([[1., 1.], [2., 5.]])
        test_loc = 0
        test_weights = np.array([0.875, 0.125])

        # Initializing model with dummy parameters
        test_model = self.gamma_mix.GammaMixModel(weights=test_weights,
                                                  params=test_params,
                                                  loc=test_loc)

        # Computing posterior probabilities manually for verification (3 steps)
        gamma_probs = np.array([test_weights[i] * gamma.pdf(
                                                   x=test_data,
                                                   a=test_params[i][0],
                                                   scale=test_params[i][1],
                                                   loc=test_loc)
                                for i in range(test_weights.size)])
        # Compute expected posteriors
        expected_posterior = gamma_probs / np.sum(gamma_probs, axis=0)

        # Compute candidate posteriors
        candidate_posterior = test_model.computePosterior(data=test_data)

        self.assertListEqual(list(expected_posterior.reshape(-1)),
                             list(candidate_posterior.reshape(-1)))
