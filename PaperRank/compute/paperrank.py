from ..util import config
from scipy import sparse
import logging
import numpy as np


def calculateStablePaperRank(M: sparse.csc_matrix, N: int) -> np.array:
    """Function to compute the stable solution to the random scholar's Markov
    process. This function implementes an adaptation of the power iteration
    method for computing the stationary distrbution for the random scholar's
    first order Markov process.
    
    Arguments:
        M {sparse.csc_matrix} -- Stochastic (i.e. Markov transition) matrix.
        N {int} -- Number of elements for which PaperRank is computed.
    
    Returns:
        np.array -- Array of PaperRanks, with indexes corresponding to M.
    """

    # Getting function configuration variables
    beta = config.compute['beta']
    epsilon = config.compute['epsilon']

    logging.info('Starting PaperRank computation for {0} IDs'.format(N))

    # Flags
    scores_old = np.repeat(1 / N, N)
    stable = False
    count = 0

    # Iterate until solution is stable
    while not stable:
        # Compute unadjusted PaperRank
        scores_unadjusted = beta * M.dot(scores_old)

        # Compute and redistribute leaked PaperRank from dangling papers
        leaked_pr = 1 - np.sum(scores_unadjusted)
        if leaked_pr > 0:
            scores = scores_unadjusted + (leaked_pr / N)

        # Compute difference between new scores and old scores
        difference = np.sum(np.absolute(scores - scores_old))
        # Update stable flag
        stable = difference < epsilon

        # Update scores_old, increment count
        scores_old = scores
        count += 1

    logging.info('Computed stable PaperRanks for {0} IDs in {1} iterations'
                 .format(N, count))

    # Return latest scores (updated in the loop)
    return scores_old
