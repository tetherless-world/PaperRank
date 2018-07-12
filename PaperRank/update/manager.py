from ..util import config
from .query import Query
from multiprocessing import Pool, Manager
from time import sleep
import logging
import os
import redis


class Manager:
    def __init__(self, conn_pool: redis.ConnectionPool,
                 recover: bool=True):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            conn_pool {ConnectionPool} -- Connection pool to be used for
                                          Database transactions.
        
        Keyword Arguments:
            recover {bool} -- True for crash recovery (default: {True}).
        """

        self.conn_pool = conn_pool

        # Creating database object for the Manager
        self.db = redis.Redis(connection_pool=self.conn_pool)

        # Recovering from failure
        if recover:
            self.recoverInstance()

        # Getting configuration information
        self.pmid_per_request = config.ncbi_api['pmid_per_request']
        self.request_per_second = config.ncbi_api['request_per_second']
        self.pmid_per_second = self.pmid_per_request * self.request_per_second
    
    def start(self):
        """Function to start scraping.
        """

        # Setting process pool size
        pool_size = os.cpu_count()

        # Creating process pool, limiting reuse
        pool = Pool(process=pool_size, maxtasksperchild=10)

        # Creating manager object, shared counter value, and lock
        m = Manager()
        proc_count = m.Value('i', 0)
        lock = m.Lock()

        # Getting initial exploration counter
        explore_count = self.getExplorationCount()

        while explore_count > 0:
            # Check if process limit is not reached
            if proc_count.value < pool_size:

                # Get PMIDs
                pmids = self.db.srandmemeber(
                    name='EXPLORE',
                    number=self.pmid_per_second)
                # Removing popped elements
                self.db.srem('EXPLORE', *pmids)
                # Adding IDs to instance nodes
                self.db.sadd('INSTANCE', *pmids)

                # Logging progress
                logging.info('Extracted {0} PubMed IDs for scraping'
                             .format(len(pmids)))

                # Acquire lock for counter
                lock.acquire()

                # Create Query workers
                while len(pmids) > 0:
                    pool.apply_async(Query, (
                        'conn_pool': self.conn_pool,
                        'pmids': pmids[0:self.pmid_per_request],
                        'proc_count': proc_count,
                        'lock': lock
                    ))
                    proc_count.value += 1
                    del pmids[0:self.pmid_per_request]

                # Release lock
                lock.release()
            
            # Check if explore count is near 0, if so update
            if explore_count < 2000:
                explore_count = self.getExplorationCount()

            # Wait for 1 second
            sleep(1)

    def recoverInstance(self):
        """Move `INSTANCE` IDs to `EXPLORE`, to recover
        from a crash/exit.
        """

        pipe = self.db.r.pipeline()
        # Move everything from `INSTANCE` to `EXPLORE`
        pipe.sunionstore('EXPLORE', 'EXPLORE', 'INSTANCE')
        # Delete `INSTANCE`
        pipe.delete('INSTANCE')
        # Execute commands
        pipe.execute()

    def getExplorationCount(self) -> int:
        """Get the number of elements remaining in the
        exploration frontier.
        
        Returns:
            int -- Number of IDs in the exploration frontier.
        """

        return int(self.db.scard('EXPLORE'))
