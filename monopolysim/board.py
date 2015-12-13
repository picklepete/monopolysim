import sys
import json
import logging
from time import sleep

from player import Player
from tiles import Tile, TaxableTile, ChanceTile, PropertyTile, \
    CommunityChestTile, JailTile, GoToJailTile, FreeParkingTile, GoTile

logging.basicConfig(format='%(levelname)s: %(message)s', filename='sim.log', level=logging.DEBUG)


class Board(object):
    """
    Represents a single Monopoly board. The board follows the following routine:

    1. The board is setup. This initializes the tiles, using the the British tile names.
    2. Each player is initialized.
    3. The banker is initialized, they deposit 1,500 into each player's wallet.
    4. Each player rolls a dice, it decides the order in which they play.
    5. Each player plays their turn...
        i) The dice are rolled.
            - If the player is in jail...

            - if the player isn't in jail...
                - If they don't roll a double...
                    - They move.
                - If they did roll a double...
                    - If a double is rolled, they can roll again.
                    - If another double is rolled, they can roll again.
                    - If a third double is rolled, they go straight to Jail.
        ii) They land on a tile.
            - If the tile is a PropertyTile
                - If the tile is owned, they pay their tax.
                - If the tile isn't owned, depending on the player's AI, it buys or skips its turn.
            - If the tile is CardTile (Chance, Community Chest)
                - It picks its card, applies its changes.
    """
    def __init__(self, num_players=4, locale='en-gb'):
        self.tiles = []
        self.players = []
        self.turn_order = {}
        self.num_players = num_players
        self.locale = locale

        # How much money the players initially receive.
        self.initial_player_deposit = 2500

    def initialize_board(self):
        """
        Reads the board JSON template for the requested locale
        and constructs the board using the relevant tiles.
        """
        logging.debug('Initializing a new board.')
        try:
            fs = open('locale/board_%s.json' % self.locale)
            board_template = json.loads(fs.read())
        except IOError:
            raise LocaleDoesNotExist('The %s locale does not have a board template.' % self.locale)

        tile_map = {
            'go': GoTile,
            'station': Tile,
            'utilities': Tile,
            'tax': TaxableTile,
            'jail': JailTile,
            'chance': ChanceTile,
            'property': PropertyTile,
            'gotojail': GoToJailTile,
            'freeparking': FreeParkingTile,
            'community_chest': CommunityChestTile
        }

        for tile_step, tile_template in enumerate(board_template):
            tile_type = tile_template['type']
            tile_template['step'] = tile_step + 1
            tile = tile_map[tile_type](**tile_template)
            self.tiles.append(tile)

    def initialize_players(self):
        """
        """
        if not len(self.tiles):
            raise RuntimeError('The board has not been initialized.')

        logging.debug('Initializing %d players.' % self.num_players)
        for pid in xrange(0, self.num_players):
            player = Player(nickname='Player%d' % pid, tile=self.tiles[0])
            player.wallet.deposit(self.initial_player_deposit)
            self.players.append(player)

    def initialize_turns(self):
        """
        Determines the order in which our players take turns. This is
        decided by rolling a die. If players have the same die value,
        they all re-roll until we have a valid sorting.
        """
        # TODO: implement this.
        pass

    def handle_turn(self, player):
        """
        Responsible for handling a player's current turn.

        1. Player rolls.
        2. Player moves to their destination tile.
        3. For each tile on the way there, they trigger on_transit.
        4. At the destination tile, player triggers on_visit.
        """
        dice_roll = player.roll_dice()
        tile_moves = sum(dice_roll)
        logging.debug('%s rolled a %d and %d.' % (player.nickname, dice_roll[0], dice_roll[1]))

        num_tiles = len(self.tiles)
        if (player.tile.step + tile_moves) > num_tiles:
            dest_tile_step = (player.tile.step + tile_moves) - num_tiles
        else:
            dest_tile_step = player.tile.step + tile_moves

        for tile in self.tiles:

            # If our roll takes us over GO, and we start board from the first tile again...
            if (player.tile.step + tile_moves) > num_tiles:
                # A valid tile is between the player's current tile, and the end of the board,
                # OR, if the tile's step is below the destination tile's step.
                valid_tile = player.tile.step <= tile.step <= num_tiles or tile.step <= dest_tile_step
            else:
                # If the roll doesn't take us across go, a valid next tile is
                # between the player's current tile and the destination tile.
                valid_tile = player.tile.step < tile.step <= dest_tile_step

            if valid_tile:
                # Have we arrived at our destination?
                if tile.step == dest_tile_step:
                    player.handle_land_on_tile(tile)
                else:
                    # For each tile, handle what happens when you transit across it.
                    player.handle_transit_tile(tile)

        # Did the player roll double die?
        if dice_roll[0] == dice_roll[1]:
            logging.debug('%s rolled a double, they get to roll again.' % player.nickname)
            self.handle_turn(player)

    def setup(self):
        self.initialize_board()
        self.initialize_players()

    def start(self):
        """
        Responsible for starting the game, taking turns, and
        looping until all but one player are bankrupt.
        """
        game_running = True
        try:
            while game_running:
                for player in self.players:
                    self.handle_turn(player)
                    sleep(2)
        except KeyboardInterrupt:
            print 'Game has been suspended.'
            sys.exit(0)


class LocaleDoesNotExist(Exception):
    """
    The requested locale does not yet exist.
    """
    pass
