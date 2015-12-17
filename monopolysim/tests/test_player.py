from unittest import TestCase

from player import Player
from board import Board


class PlayerTestCase(TestCase):

    def _mock_roll_dice_single(self):
        return 1, 2

    def _mock_roll_dice_double(self):
        return 1, 1

    def test_player_deposit_cash(self):
        player = Player(cash=0)
        player.wallet.deposit(500)
        self.assertEqual(player.cash, 500)

    def test_player_withdraw_cash(self):
        player = Player(cash=500)
        player.wallet.withdraw(500)
        self.assertEqual(player.cash, 0)

    def test_player_triple_double_roll_move_to_jail(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        setattr(player, '_roll_dice', self._mock_roll_dice_double)

        player.roll_dice()
        self.assertFalse(player.in_jail)
        self.assertEqual(len(player.dice_roll_history), 1)

        player.roll_dice()
        self.assertFalse(player.in_jail)
        self.assertEqual(len(player.dice_roll_history), 2)

        player.roll_dice()
        self.assertTrue(player.in_jail)
        self.assertEqual(player.tile.name, 'Jail')
        self.assertEqual(len(player.dice_roll_history), 0)

    def test_jailed_player_triple_double_roll_dont_move_to_jail(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        player.handle_jail_entry()
        self.assertTrue(player.in_jail)
        setattr(player, '_roll_dice', self._mock_roll_dice_double)

        player.roll_dice()
        self.assertTrue(player.in_jail)
        self.assertEqual(len(player.dice_roll_history), 1)

        player.roll_dice()
        self.assertTrue(player.in_jail)
        self.assertEqual(len(player.dice_roll_history), 2)

        player.roll_dice()
        self.assertTrue(player.in_jail)
        self.assertEqual(player.tile.name, 'Jail')
        self.assertEqual(len(player.dice_roll_history), 0)
