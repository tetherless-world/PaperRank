from ..util import config
from .query import Query
from multiprocessing import Pool, Value, Lock
from multiprocessing import Manager as ProcManager
from time import sleep
import logging
import os
from redis import ConnectionPool, StrictRedis


class Manager:
    def __init__(self, conn_pool: ConnectionPool,
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
        self.db = StrictRedis(connection_pool=self.conn_pool)

        # Recovering from failure
        if recover:
            self.recoverInstance()

        # Cleaning EXPLORE
        self.cleanExplore()        

        # Getting configuration information
        self.pmid_per_request = config.ncbi_api['pmid_per_request']
        self.request_per_second = config.ncbi_api['request_per_second']
        self.pmid_per_second = self.pmid_per_request * self.request_per_second

        # Setting pool size and maxtasksperchild
        self.pool_size = os.cpu_count() * 20
        self.maxtasksperchild = 10

        # Setting clean interval, every 1000 cycles
        self.clean_interval = 1000

    def start(self):
        """Function to start scraping.
        """

        # Creating initial process pool
        (pool, m, proc_count, lock) = self.createProcessPoolObjects()

        # Getting initial exploration counter
        explore_count = self.getExplorationCount()

        counter = 0

        while explore_count > 0:
            # Check if process limit is not reached
            if proc_count.value < self.pool_size:
                # Get PMIDs
                pmids = self.db.srandmember(
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

                # Reducing explore_count, increment counter
                explore_count -= len(pmids)
                counter += 1

                # Create Query workers
                while len(pmids) > 0:
                    pool.apply_async(Query, (
                        False,
                        pmids[0:self.pmid_per_request],
                        proc_count,
                        lock
                    ))
                    proc_count.value += 1
                    del pmids[0:self.pmid_per_request]

                # Log stuff
                logging.info('Currently running {0} Query processes'
                             .format(proc_count.value))
                logging.info('There are {0} PMIDs left in EXPLORE size cache'
                             .format(explore_count))
                logging.info(
                    'Currently on cycle {0} with {1} left before process clean'
                    .format(
                        counter,
                        self.clean_interval - counter))

                # Release lock
                lock.release()

                # Also close and re-create pool
                if counter >= self.clean_interval:
                    # Clean and recreate process pool
                    (pool, m, proc_count, lock) = self.cleanProcessPool(
                        pool=pool,
                        proc_count=proc_count)
                    # Clean EXPLORE
                    self.cleanExplore()
                    # Reset counter
                    counter = 0

            # Check if explore count is near 0, if so update
            if explore_count < self.pmid_per_request:
                explore_count = self.getExplorationCount()

            # Wait for 1 second
            sleep(1)

    def recoverInstance(self):
        """Move `INSTANCE` IDs to `EXPLORE`, to recover
        from a crash/exit.
        """
        logging.info('Recovering {0} IDs from INSTANCE'
                     .format(self.db.scard('INSTANCE')))
        pipe = self.db.pipeline()
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

    def cleanExplore(self):
        """Function to clean EXPLORE, by removing all items already
        in SEEN.
        """

        # Logging before
        logging.info('{0} PMIDs in Explore and {1} PMIDs in SEEN before clean'
                     .format(self.db.scard('EXPLORE'), self.db.scard('SEEN')))
        # Removing SEEN IDs from EXPLORE
        logging.info('Removing SEEN IDs from EXPLORE')
        self.db.sdiffstore('EXPLORE', 'EXPLORE', 'SEEN')
        # Logging after
        logging.info('{0} PMIDs in Explore and {1} PMIDs in SEEN after clean'
                     .format(self.db.scard('EXPLORE'), self.db.scard('SEEN')))

    def cleanProcessPool(self, pool: Pool, proc_count: Value) \
            -> (Pool, ProcManager, Value, Lock):
        """Function to close the current process pool and return new Process
        pool objects.
        
        Arguments:
            pool {Pool} -- Current process pool.
            proc_count {Value} -- Current process counter.
        
        Returns:
            Pool, ProcManager, Value, Lock -- New process pool objects.
        """

        logging.info('Cleaning process pool with {0} processes'
                     .format(proc_count.value))
        # Closing pool
        pool.close()
        # Joining processes
        logging.info('Waiting for {0} processes to join'
                     .format(proc_count.value))
        pool.join()
        self.recoverInstance()
        return self.createProcessPoolObjects()
    
    def createProcessPoolObjects(self) -> (Pool, ProcManager, Value, Lock):
        """Function to return new Process Pool objects; a new Pool, ProcManager,
        Value (proc_counter) and Lock.
        
        Returns:
            Pool, ProcManager, Value, Lock -- New process pool objects.
        """

        logging.info('Creating new process pool with {0} workers'
                     .format(self.pool_size))
        pool = Pool(processes=self.pool_size,
                    maxtasksperchild=self.maxtasksperchild)
        logging.info('Creating new multiprocessing.Manager object')
        m = ProcManager()
        logging.info('Creating new proc_count at 0')
        proc_count = m.Value('i', 0)
        logging.info('Creating new lock object')
        lock = m.Lock()
        return (pool, m, proc_count, lock)
