#!/usr/bin/env python

from board import Board

if __name__ == '__main__':
    game = Board(num_players=1)
    game.setup()
    game.start()
