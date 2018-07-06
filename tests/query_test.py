from context import PaperRank

import unittest


class TestQuery(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """Override initialization function to setup PaperRank config.
        """

        super(TestQuery, self).__init__(*args, **kwargs)
        PaperRank.util.configSetup()
        self.config = PaperRank.util.config

    def test_init(self):
        """Test intialization of Query object.
        """

        PaperRank.util.configSetup()
        config = PaperRank.util.config
        db = PaperRank.util.Database(
            host=self.config.test['redis']['host'],
            port=self.config.test['redis']['port'],
            db=self.config.test['redis']['db'])
        test = PaperRank.update.Query(db=db,
                                      pmids=[21876761, 21876726, 29409535],
                                      suppress_worker=True)
        self.assertTrue(True)
