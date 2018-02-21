"""Test requirement methods."""
from os.path import join


def get_testpath(filename):
    """Get testfile path."""
    return join('tests', join('samples', filename))
