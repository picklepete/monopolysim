#!/usr/bin/env python

from unittest import TestLoader, TextTestRunner, TestSuite
from tests.test_board import BoardTestCase
from tests.test_player import PlayerTestCase
from tests.test_tiles import TileTestCase


if __name__ == "__main__":
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(BoardTestCase),
        loader.loadTestsFromTestCase(PlayerTestCase),
        loader.loadTestsFromTestCase(TileTestCase)
    ))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
