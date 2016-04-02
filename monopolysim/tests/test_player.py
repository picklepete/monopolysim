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

    def test_get_portfolio(self):
        board = Board(num_players=1, locale='en-gb')
        board.setup()

        player = board.players[0]
        player.wallet.deposit(5000)

        for name in ['Old Kent Road', 'Whitechapel Road', 'Liverpool Street Station']:
            tile = board.get_tile_by_name(name)
            player.purchase_property(tile)

        portfolio = player.get_portfolio()

        self.assertIn('station', portfolio)
        self.assertEqual(len(portfolio['station']), 1)
        self.assertIn('brown', portfolio)
        self.assertEqual(len(portfolio['brown']), 2)

    def test_pay_rent(self):
        board = Board(num_players=2, locale='en-gb')
        board.setup()

        p1 = board.players[0]
        p1_cash = p1.cash
        p2 = board.players[1]
        p2_cash = p2.cash

        owned_tile = board.get_tile_by_name('Mayfair')
        owned_tile.owner = p1
        rent = owned_tile.get_rent_cost()

        p2.pay_rent(owned_tile, rent)

        self.assertEqual(p1.cash, p1_cash + rent)
        self.assertEqual(p2.cash, p2_cash - rent)
