from context import PaperRank

import unittest


class TestQuery(unittest.TestCase):
    """Tests for the Query and Worker modules.
    """

    def __init__(self, *args, **kwargs):
        """Override initialization function to setup PaperRank config.
        """

        super(TestQuery, self).__init__(*args, **kwargs)
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config
        self.db = PaperRank.util.Database(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db'])

    def test_init(self):
        """Test Query and Worker objects.
        """

        # Flush test database (manual access)
        self.db.r.flushdb()

        # Testing Query module
        PaperRank.update.Query(db=self.db,
                               pmids=[21876761, 21876726, 29409535, 29025144])
        # Testing behavior with invalid IDs
        PaperRank.update.Query(db=self.db, pmids=['sdfgsdg'])
        
        dangling_count = self.db.size(database='D')
        seen_count = self.db.size(database='S')

        # Note: As this is a clean database, the number of
        # tuples added to `GRAPH` should be equal to the number of
        # IDs added to `EXPLORE`, as they are all not in `SEEN`. This implies
        # that their difference should be 0, and not affect the sum of the
        # number of IDs in `DANGLING` and the number of IDs in `SEEN`
        explore_graph_diff = self.db.size(database='G') \
            - self.db.size(database='E')

        self.assertEqual(dangling_count + seen_count + explore_graph_diff, 5)

        # Flush test database again (manual access)
        self.db.r.flushdb()
