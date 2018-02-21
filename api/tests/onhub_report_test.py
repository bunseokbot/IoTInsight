"""Test for onhub diagnostic report parser."""
import unittest

from tests import get_testpath
from parsers.onhub import Onhub


class OnhubParseTestCase(unittest.TestCase):
    """Onhub parse testcase."""

    def setUp(self):
        """Setup testcase."""
        self.filepath = get_testpath('test.report')
        self.onhub = Onhub(self.filepath)

    def test_load_report(self):
        """Test to load onhub report."""
        self.assertTrue(self.onhub)

    def test_load_time(self):
        """Test to parse time from json report."""
        self.onhub.report['unixTime']

    def tearDown(self):
        """End onhub parse testcase."""
        del self
