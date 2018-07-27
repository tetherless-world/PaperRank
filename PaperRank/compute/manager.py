from .paperrank import calculateStablePaperRank
from .util import buildOutDegreeMap
from .stochastic_matrix import constructStochasticMatrix
from ..util import config

from redis import StrictRedis
import logging
import numpy as np


class Manager:
    def __init__(self, r: StrictRedis):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.
        """

        # Compute engine settings
        self.log_increment_percent = 0.5

        # Class variables
        self.r = r
        self.N = self.r.scard('SEEN')
        self.log_increment = (self.N / 100) * self.log_increment_percent

        logging.info('Initializing with {0} IDs in SEEN'.format(self.N))

        # Building out degree map
        logging.info('Building out degree map')
        buildOutDegreeMap(r=self.r)

    def start(self, cutoff: int=None):
        """Function to start the PaperRank computation.
        
        Keyword Arguments:
            cutoff {int} -- Optional iteration cutoff. (default: {None})
        """

        # Startup
        logging.info('Starting PaperRank computation for {0} IDs'
                     .format(self.N))

        # Copying seen IDs
        logging.info('Copying {0} IDs from SEEN'
                     .format(self.r.scard('SEEN')))
                     
        seen = np.array(list(self.r.smembers('SEEN')), dtype=np.int)
        seen_sorted = np.sort(seen)[::-1]  # Sorting in ascending and reverse
        
        logging.info('Successfully extracted and sorted {0} IDs from SEEN'
                     .format(seen_sorted.size))

        if cutoff:
            logging.info('Cutoff set at {0}'.format(cutoff))
            # Isolating seen_sorted IDs
            seen_sorted = seen_sorted[0:cutoff]
            # Updating self.N
            self.N = seen_sorted.size
            logging.info('Reducing PaperRank computation to {0} IDs'
                         .format(cutoff))
        
        M = constructStochasticMatrix(r=self.r, seen=seen_sorted)

        paperrank = calculateStablePaperRank(M, self.N)

        logging.info('Computed PaperRanks for {0} IDs'.format(self.N))

        return paperrank

    def __logProgress(self):
        """Function to log the progress of PaperRank computation.
        """

        if (self.__count - self.__last_check) > self.log_increment:
            self.__last_check = self.__count
            logging.info('PaperRank computation {0}% complete'.format(
                round(self.__count / self.N, 3) * 100))
