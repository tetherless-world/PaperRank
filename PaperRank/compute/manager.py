from .paperrank import StablePaperRank
from .util import buildOutDegreeMap, buildIdList
from .stochastic_matrix import constructStochasticMatrix
from ..util import config

from redis import StrictRedis
import logging
import numpy as np


class Manager:
    def __init__(self, r: StrictRedis, cutoff: int=None):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.
        
        Keyword Arguments:
            cutoff {int} -- ID number limit. (default: {None})
        """

        # Class variables
        self.r = r

        # Intializing SEEN ID list
        logging.info('Initializing with {0} IDs in SEEN'
                     .format(r.scard('SEEN')))
        self.seen = buildIdList(r=self.r, cutoff=cutoff)
        self.N = self.seen.size

        # Building out degree map
        logging.info('Building out degree map')
        buildOutDegreeMap(r=self.r)

        # Logging configuration
        self.log_increment_percent = 0.5
        self.log_increment = (self.N / 100) * self.log_increment_percent

    def start(self):
        """Function to start the PaperRank computation.
        """

        # Startup
        logging.info('Starting PaperRank computation for {0} IDs'
                     .format(self.N))
        
        M = constructStochasticMatrix(r=self.r, seen=self.seen)

        # Initializing StablePaperRank object
        compute_engine = StablePaperRank(M, self.N)
        # Computing PaperRanks
        paperrank = compute_engine.calculate()

        logging.info('Computed PaperRanks for {0} IDs'.format(self.N))

        return paperrank
