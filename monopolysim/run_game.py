#!/usr/bin/env python

from optparse import OptionParser
from board import Board

parser = OptionParser()
parser.add_option('-p', '--players', action='store', type='int',
                  default=2, help='The total number of players.', dest='players')
parser.add_option('-l', '--locale', action='store', type='string',
                  default='en-gb', help='The Monopoly board game locale.', dest='locale')
parser.add_option('-f', '--fast', action='store_true', default=False, help='Play the game in fast mode.', dest='fast')
(options, args) = parser.parse_args()


if __name__ == '__main__':
    game = Board(num_players=options.players, locale=options.locale, fast=options.fast)
    game.setup()
    game.start()
