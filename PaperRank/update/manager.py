from ..util import config, Database
from .query import Query
from time import sleep
import logging
import threading


class Manager:
    def __init__(self, db: Database, recover: bool=True):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            db {Database} -- Database to be used for data transactions.
        
        Keyword Arguments:
            recover {bool} -- True for crash recovery (default: {True}).
        """

        self.db = db

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

        while not self.db.isEmpty(database='E'):
            # Isolate PMIDs 
            pmids = self.db.pop(database='E', n=self.pmid_per_second)
            # Logging progress
            logging.info('Extracted {0} PubMed IDs for scraping'
                         .format(len(pmids)))
            # Loop through until empty
            while len(pmids) > 0:
                # Spawn thread with Query worker, and PMIDs
                threading.Thread(target=Query, kwargs={
                    'db': self.db,
                    'pmids': pmids[0:self.pmid_per_request]
                }).start()
                # Logging progress
                logging.info('Spawned Query thread with {0} PubMed IDs'
                             .format(len(pmids[0:self.pmid_per_request])))
                # Remove used PMIDs from list
                del pmids[0:self.pmid_per_request]
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
        pipe.delete('THIS SHOULD FAIL')
        # Execute commands
        pipe.execute()
