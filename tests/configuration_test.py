from context import PaperRank

import unittest


class TestConfiguration(unittest.TestCase):
    """Tests for the `configuration` module.
    """

    def test_noOverride(self):
        """Testing the configuration variable initialization without overriding
        any settings.
        """

        PaperRank.configSetup()
        self.assertEqual(PaperRank.config.redis['host'], 'localhost')

    def test_withOverride(self):
        """Testing the configuration variable intialization with setting
        override.
        """

        PaperRank.configSetup(override='test.json')
        self.assertEqual(PaperRank.config.redis['host'], 'test')
