from unittest import TestCase

from board import Board, LocaleDoesNotExist


class BoardTestCase(TestCase):

    def test_board_initialize_invalid_locale(self):
        with self.assertRaises(LocaleDoesNotExist):
            board = Board(locale='en-us')
            board.initialize_board()

    def test_board_initialize_en_gb(self):
        board = Board(locale='en-gb')
        board.initialize_board()
        self.assertEqual(len(board.tiles), 40)

    def test_board_initialize_players_with_no_tiles(self):
        with self.assertRaises(RuntimeError):
            board = Board(locale='en-gb')
            board.initialize_players()

    def test_board_initialize_players(self):
        board = Board(num_players=2, locale='en-gb')
        board.initialize_board()
        board.initialize_players()
        self.assertEqual(len(board.players), 2)
        for player in board.players:
            self.assertEqual(player.cash, board.initial_player_deposit)
            self.assertEqual(player.tile.step, 1)

    def test_board_handle_non_circular_turn(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()
        player = board.players[0]



