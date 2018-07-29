from context import PaperRank

from multiprocessing import Manager, Pool
from redis import ConnectionPool, StrictRedis

import unittest


class TestUpdateEngine(unittest.TestCase):
    """Tests for the Query and Worker modules.
    """

    def __init__(self, *args, **kwargs):
        """Override initialization function to setup PaperRank config.
        """

        super(TestUpdateEngine, self).__init__(*args, **kwargs)
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

        self.conn_pool = ConnectionPool(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db']
        )

        # Creating process pool
        self.pool = Pool(processes=10, maxtasksperchild=10)

        # Creating manager object, shared counter value and lock
        self.m = Manager()
        self.proc_count = self.m.Value('i', 0)
        self.lock = self.m.Lock()

    def test_query_and_worker(self):
        """Test Query and Worker objects.
        """

        # Flush test database (manual access)
        r = StrictRedis(connection_pool=self.conn_pool)
        r.flushdb()

        # Testing Query module
        PaperRank.update.Query(conn_pool=self.conn_pool,
                               pmids=[21876761, 21876726, 29409535, 29025144],
                               proc_count=self.proc_count,
                               lock=self.lock)
        # Testing behavior with invalid IDs
        PaperRank.update.Query(conn_pool=self.conn_pool,
                               pmids=['sdfgsdg'],
                               proc_count=self.proc_count,
                               lock=self.lock)
        
        dangling_count = r.scard(name='DANGLING')
        seen_count = r.scard('SEEN')

        # Note: As this is a clean database, the number of
        # tuples added to `GRAPH` should be equal to the number of
        # IDs added to `EXPLORE`, as they are all not in `SEEN`. This implies
        # that their difference should be 0, and not affect the sum of the
        # number of IDs in `DANGLING` and the number of IDs in `SEEN`
        explore_graph_diff = r.scard(name='GRAPH') - r.scard(name='EXPLORE')

        self.assertEqual(dangling_count + seen_count + explore_graph_diff, 5)

        # Flush test database again (manual access)
        r.flushdb()
