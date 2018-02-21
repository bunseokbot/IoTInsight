"""Test for packet parse."""
import unittest

from tests import get_testpath
from parsers.packet import Packet


class PacketParseTestCase(unittest.TestCase):
    """Packet parse testcase."""

    def setUp(self):
        """Setup testcase."""
        self.filepath = get_testpath('test.tcpdump')
        self.packet = Packet(self.filepath)

    def test_load_packet(self):
        """Check packet parser load normally."""
        self.assertTrue(self.packet)

    def test_read_packet(self):
        """Check read packet normally."""
        self.packet.packets[0]

    def tearDown(self):
        """End packet parse testcase."""
        del self
