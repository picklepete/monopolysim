#!/usr/bin/env python

from unittest import TestLoader, TextTestRunner, TestSuite
from tests.test_board import BoardTestCase
from tests.test_player import PlayerTestCase


if __name__ == "__main__":
    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(BoardTestCase),
        loader.loadTestsFromTestCase(PlayerTestCase)
    ))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
