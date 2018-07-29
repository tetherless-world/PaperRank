from ..util import config

from scipy import sparse
import logging
import numpy as np


class StablePaperRank:
    def __init__(self, M: sparse.csc_matrix, N: int):
        """Initialization logic for the StablePaperRank submodule.
        
        Arguments:
            M {sparse.csc_matrix} -- Stochastic (Markov transition) matrix.
            N {int} -- Number of elements for which PaperRank is computed.
        """

        # Configuration variables
        self.beta = config.compute['beta']
        self.epsilon = config.compute['epsilon']

        # Storing input parameters
        self.M = M
        self.N = N

        logging.info('Initialized StablePaperRank module with {0} IDs'
                     .format(self.N))

    def calculate(self) -> np.array:
        """Function to compute the stable solution to the random scholar's
        Markov process. This function implements an adaptation of the power
        iteration method for computing the stationary distrbution for the
        random scholar's first order Markov process.

        Returns:
            np.array -- Array of PaperRanks, with indexes corresponding to M.
        """

        logging.info('Computing stable PaperRank solution for {0} IDs'
                     .format(self.N))

        # Flags
        scores_old = np.repeat(1 / self.N, self.N)
        stable = False
        count = 0

        # Iterate until solution is stable
        while not stable:
            # Compute unadjusted PaperRank
            scores_unadjusted = self.beta * self.M.dot(scores_old)

            # Compute and redistribute leaked PaperRank from dangling papers
            leaked_pr = 1 - np.sum(scores_unadjusted)
            if leaked_pr > 0:
                scores = scores_unadjusted + (leaked_pr / self.N)

            # Compute difference between new scores and old scores
            difference = np.sum(np.absolute(scores - scores_old))
            # Update stable flag
            stable = difference < self.epsilon

            # Update scores_old, increment count
            scores_old = scores
            count += 1

            # Logging
            logging.info('Completed {0} compute iterations with difference {1}'
                         .format(count, difference))

        logging.info('Computed stable PaperRanks for {0} IDs in {1} iterations'
                     .format(self.N, count))

        # Return latest scores (updated in the loop)
        return scores_old
    