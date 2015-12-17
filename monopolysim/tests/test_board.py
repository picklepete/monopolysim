from unittest import TestCase

from tiles import Tile
from board import Board, LocaleDoesNotExist


class BoardTestCase(TestCase):

    def _mock_roll_dice_single(self):
        return 1, 2

    def _mock_roll_dice_double(self):
        return 1, 1

    def _mock_handle_play_turn_noop(self, *args, **kwargs):
        pass

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

    def test_board_get_real_tile_by_name(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()
        tile = board.get_tile_by_name('Jail')
        self.assertIsInstance(tile, Tile)
        self.assertEqual(tile.name, 'Jail')

    def test_board_get_fake_tile_by_name(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()
        tile = board.get_tile_by_name('Buckingham Palace')
        self.assertIsNone(tile)

    def test_board_handle_non_circular_turn(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()
        player = board.players[0]

    def test_board_handle_jail_turn_exit_pay(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        player.handle_jail_entry()

        def mock_jail_exit_choice():
            return 'pay'
        setattr(player, 'jail_exit_choice', mock_jail_exit_choice)

        previous_cash = player.cash
        board.handle_jail_turn(player)
        self.assertFalse(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 0)
        self.assertEqual(player.cash, previous_cash - 50)

    def test_board_handle_jail_turn_exit_full_duration(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        player.handle_jail_entry()

        def mock_jail_exit_choice():
            return 'wait'

        setattr(player, 'roll_dice', self._mock_roll_dice_single)
        setattr(player, 'jail_exit_choice', mock_jail_exit_choice)

        board.handle_jail_turn(player)
        self.assertTrue(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 1)

        board.handle_jail_turn(player)
        self.assertTrue(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 2)

        board.handle_jail_turn(player)
        self.assertTrue(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 3)

        previous_cash = player.cash
        board.handle_jail_turn(player)
        self.assertFalse(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 0)
        self.assertEqual(player.cash, previous_cash - 50)

    def test_board_handle_jail_turn_exit_short_duration(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        player.handle_jail_entry()

        def mock_jail_exit_choice():
            return 'wait'

        setattr(player, 'roll_dice', self._mock_roll_dice_single)
        setattr(player, 'jail_exit_choice', mock_jail_exit_choice)

        # Mock handle_play_turn, or a maximum recursion depth exceeded
        # exception is thrown because the rules dictate that a  double
        # dice roll results in another turn, so handle_play_turn is
        # looped indefinitely.
        setattr(board, 'handle_play_turn', self._mock_handle_play_turn_noop)

        board.handle_jail_turn(player)
        self.assertTrue(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 1)

        setattr(player, 'roll_dice', self._mock_roll_dice_double)

        board.handle_jail_turn(player)
        self.assertFalse(player.in_jail)
        self.assertEqual(player.jail_exit_rolls, 0)
