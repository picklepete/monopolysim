from unittest import TestCase

from board import Board


class TileTestCase(TestCase):

    def test_unowned_is_owned(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        tile = board.get_tile_by_name('Mayfair')
        self.assertFalse(tile.is_owned)

    def test_owned_is_owned(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        tile = board.get_tile_by_name('Mayfair')
        tile.owner = player
        self.assertTrue(tile.is_owned)

    def test_house_get_upgrade_price(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        tile = board.get_tile_by_name('Mayfair')
        self.assertEqual(tile.houses, 0)
        upgrade_type, upgrade_price = tile.get_upgrade_price()
        self.assertEqual(upgrade_type, 'house')
        self.assertEqual(upgrade_price, 200)

    def test_hotel_get_upgrade_price(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        tile = board.get_tile_by_name('Mayfair')
        tile.houses = 4
        upgrade_type, upgrade_price = tile.get_upgrade_price()
        self.assertEqual(upgrade_type, 'hotel')
        self.assertEqual(upgrade_price, 200)

    def test_house_property_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        tile = board.get_tile_by_name('Mayfair')
        tile.houses = 3
        rent = tile.get_rent_cost((1, 1))
        self.assertEqual(rent, 1400)

    def test_hotel_property_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        tile = board.get_tile_by_name('Mayfair')
        tile.hotel = True
        rent = tile.get_rent_cost((1, 1))
        self.assertEqual(rent, 2000)

    def test_single_station_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        tile = board.get_tile_by_name('Marylebone Station')
        tile.owner = player
        rent = tile.get_rent_cost((1, 1))
        self.assertEqual(rent, 25)

    def test_double_station_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        marylebone = board.get_tile_by_name('Marylebone Station')
        marylebone.owner = player
        fenchurch = board.get_tile_by_name('Fenchurch St Station')
        fenchurch.owner = player
        rent = marylebone.get_rent_cost((1, 1))
        self.assertEqual(rent, 50)

    def test_single_utility_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        tile = board.get_tile_by_name('Water Works')
        tile.owner = player
        dice_roll = (5, 5)
        expected_rent = sum(dice_roll) * 4
        rent = tile.get_rent_cost(dice_roll)
        self.assertEqual(rent, expected_rent)

    def test_double_utility_get_rent_cost(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        water = board.get_tile_by_name('Water Works')
        water.owner = player
        electric = board.get_tile_by_name('Electric Company')
        electric.owner = player
        dice_roll = (3, 6)
        expected_rent = sum(dice_roll) * 10
        rent = water.get_rent_cost(dice_roll)
        self.assertEqual(rent, expected_rent)

    def test_taxable_tile(self):
        board = Board(locale='en-gb', num_players=1)
        board.setup()
        player = board.players[0]
        initial_cash = player.cash
        player.tile = board.get_tile_by_name('Old Kent Road')
        board.handle_play_turn(player, (1, 2))
        self.assertTrue(player.tile.name, 'Income Tax')
        self.assertEqual(player.cash, initial_cash - 200)

