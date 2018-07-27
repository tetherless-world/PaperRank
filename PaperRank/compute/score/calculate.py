from .iteration_score import computeIterationScore
from ...util import config
from redis import StrictRedis
import logging
import numpy as np


def calculate(r: StrictRedis, id_list: np.array):
    """Function to compute the stable solution for a given list of IDs.
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
        id_list {np.array} -- List of IDs for stable PaperRank computation.
    """

    # Getting function variables
    N = id_list.size
    epsilon = config.compute['epsilon']

    logging.info('Calculating stable PaperRank for {0} IDs'.format(N))

    # flags
    scores_old = np.repeat((1 / N), N)
    stable = False

    # Iterate until solution is stable
    while not stable:
        scores_new = computeIterationScore(r=r, id_list=id_list)
        scores_old = np.copy(scores_new)

        # Check if the solution is stable
        difference = np.sum(np.absolute(scores_new - scores_old))
        stable = difference < epsilon
