from unittest import TestCase

from player import Player


class PlayerTestCase(TestCase):

    def test_player_deposit_cash(self):
        player = Player(cash=0)
        player.wallet.deposit(500)
        self.assertEqual(player.cash, 500)

    def test_player_withdraw_cash(self):
        player = Player(cash=500)
        player.wallet.withdraw(500)
        self.assertEqual(player.cash, 0)

