from .util import buildOutDegreeMap
from .score import calculate, computeIterationScore
from ..util import config

from redis import StrictRedis
import logging
import numpy as np


class Manager:
    def __init__(self, r: StrictRedis, recover: bool=True):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.

        Keyword Arguments:
            recover {bool} -- True for crash recovery (default: {True}).
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

        # Recover from crash
        self.seen = self.__crashRecover() if recover else np.array([])

    def start(self, cutoff: int=None):
        """Function to start the PaperRank computation.
        
        Keyword Arguments:
            cutoff {int} -- Optional iteration cutoff. (default: {None})
        """

        # Startup
        logging.info('Starting PaperRank computation for {0} IDs'
                     .format(self.N))

        if cutoff:
            logging.info('Cutoff set at {0}'.format(cutoff))

        # counters
        self.__count = 0
        self.__last_check = 0

        # # Iterate through list
        # for candidate_id in reversed(range(self.id_limit)):
        #     # Check if ID exists in self.seen and SEEN in Redis
        #     is_id = self.r.sismember('SEEN', candidate_id)
        #     is_seen = np.in1d(candidate_id, self.seen)

        #     if is_id and not is_seen:
        #         # Append to front so missed lookups are minimized
        #         self.id_list = np.append(str(candidate_id), self.id_list)

        #         # Compute PaperRank for self.id_list
        #         calculate(r=self.r, id_list=self.id_list)

        #         # Increment count, log
        #         self.__count += 1
        #         self.__logProgress()

        #         # Check cutoff
        #         if self.__count == cutoff:
        #             logging.info('Cutoff reached, exiting')
        #             break

        seen_ids = np.array(list(self.r.smembers('SEEN')), dtype=int)
        seen_ids_sorted = np.array(np.sort(seen_ids)[::-1], dtype=str)
        if cutoff:
            seen_ids_sorted = seen_ids_sorted[0:cutoff]
        computeIterationScore(r=self.r, id_list=seen_ids_sorted)
        calculate(r=self.r, id_list=seen_ids_sorted)

    def __logProgress(self):
        """Function to log the progress of PaperRank computation.
        """

        if (self.__count - self.__last_check) > self.log_increment:
            self.__last_check = self.__count
            logging.info('PaperRank computation {0}% complete'.format(
                round(self.__count / self.N, 3) * 100))

    def __crashRecover(self) -> np.array:
        """Function to recover from crash and build array of IDs already seen.
        
        Returns:
            np.array -- Array of IDs already seen.
        """

        existing_pr = self.r.hkeys('PaperRank')
        seen = np.array(existing_pr, dtype='int')
        return seen
