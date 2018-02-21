"""Utility modules."""
from datetime import datetime


def convert_time(timestamp):
    """Convert timestamp to datetime."""
    return datetime.utcfromtimestamp(timestamp)


def convert_macaddr(addr):
    """Convert mac address to unique format."""
    return addr.replace(':', '').lower()
