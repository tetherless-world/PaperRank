from .util import buildOutDegreeMap, constructStochasticMatrix
from .score import calculate, computeIterationScore
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
        self.id_limit = config.compute['id_limit']  # ID to count down from

        self.log_increment_percent = 0.5

        # Class variables
        self.r = r
        self.id_list = np.array([], dtype=str)
        self.N = self.r.scard('SEEN')
        self.log_increment = (self.N / 100) * self.log_increment_percent

        # Building out degree map, if necessary
        if self.r.hlen('OUT') != self.r.hlen('OUT_DEGREE'):
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
            logging.info('Reducing PaperRank computation to {0} IDs'
                         .format(cutoff))
        
        M = constructStochasticMatrix(r=self.r, seen=seen_sorted)

    def __logProgress(self):
        """Function to log the progress of PaperRank computation.
        """

        if (self.__count - self.__last_check) > self.log_increment:
            self.__last_check = self.__count
            logging.info('PaperRank computation {0}% complete'.format(
                round(self.__count / self.N, 3) * 100))
