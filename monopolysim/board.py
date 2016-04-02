import sys
import json
import logging
from time import sleep
from random import randint

from player import Player
from conf import MAX_JAIL_FAILED_ROLLS, PLAYER_JAIL_PAY, \
    PLAYER_JAIL_WAIT, DEFAULT_PLAYER_NAMES
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

        # The total number of tiles on the board.
        self.total_tile_count = 0

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
            tile_template['board'] = self
            tile_template['step'] = tile_step + 1
            tile = tile_map[tile_type](**tile_template)
            self.tiles.append(tile)

        # Update the total tile count.
        self.total_tile_count = len(self.tiles)

    def initialize_players(self):
        """
        """
        if not len(self.tiles):
            raise RuntimeError('The board has not been initialized.')

        logging.debug('Initializing %d players.' % self.num_players)
        for pid in xrange(0, self.num_players):
            nickname = self.get_random_player_name(pid)
            player = Player(nickname=nickname, tile=self.tiles[0])
            self.players.append(player)

    def initialize_turns(self):
        """
        Determines the order in which our players take turns. This is
        decided by rolling a die. If players have the same die value,
        they all re-roll until we have a valid sorting.
        """
        # TODO: implement this.
        pass

    def get_tile_by_name(self, name):
        """
        Returns the `Tile` in `self.tiles` which has a name of `name`.
        """
        for tile in self.tiles:
            if tile.name == name:
                return tile
        return None

    def get_random_player_name(self, pid, database=None):
        """
        Picks a random name from the `database` list, and
        if it's not set, defaults to DEFAULT_PLAYER_NAMES.
        """
        if database is None:
            database = DEFAULT_PLAYER_NAMES
        used_player_names = map(lambda player: player.nickname, self.players)
        available_names = list(set(database) - set(used_player_names))
        if available_names:
            return available_names[randint(0, len(available_names) - 1)]
        return 'Player%d' % pid

    def handle_jail_turn(self, player):
        """
        A player can exit jail under four conditions:

        1. Pay a fine of 50 and continue on their next turn
        2. Purchase a "Get Out Of Jail Free" card from another player
        3. Use a "Get Out Of Jail Free" card if they have one
        4. Wait there for three turns, rolling the dice on each turn to try to roll a double.
           If they roll a double on any turn, move out of Jail using this dice roll. After they
           have waited three turns, they must move out of Jail and pay 50 before moving their
           token according to their dice roll.

        As we want to support multiple player decisions, we'll call the player's jail_exit_choice
        method, which will return a decision based on the player (eventual) AI. This decision will
        then make us pick one of the four conditions.
        """
        turn_decision = player.jail_exit_choice()
        if turn_decision == PLAYER_JAIL_PAY:
            player.wallet.withdraw(50)
            player.handle_jail_exit()
        elif turn_decision == PLAYER_JAIL_WAIT:
            if player.jail_exit_rolls == MAX_JAIL_FAILED_ROLLS:
                player.wallet.withdraw(50)
                player.handle_jail_exit()
                logging.debug('%s has been in jail for %s turns, they '
                              'are now free.' % (player.nickname, MAX_JAIL_FAILED_ROLLS))
                return self.handle_play_turn(player)

            dice_roll = player.roll_dice()
            if dice_roll[0] == dice_roll[1]:
                logging.debug('%s rolled a %d and %d, they exit jail.' % (
                    player.nickname,
                    dice_roll[0],
                    dice_roll[1]
                ))
                player.handle_jail_exit()
                return self.handle_play_turn(player, dice_roll)

            player.jail_exit_rolls += 1
            logging.debug('%s rolled a %d and %d. They remain in jail (roll %d of %d).' % (
                player.nickname,
                dice_roll[0],
                dice_roll[1],
                player.jail_exit_rolls,
                MAX_JAIL_FAILED_ROLLS
            ))

    def handle_play_turn(self, player, dice_roll=None):
        """
        Responsible for handling a player's current turn.
        """
        # Let the player decide if they wish to purchase houses or hotels.
        player.construct_houses()

        # If a dice roll hasn't been given to it, roll.
        if not dice_roll:
            dice_roll = player.roll_dice()
            if dice_roll is None:
                # The player has rolled three doubles in a roll.
                return

        # Count the number of tiles we're moving.
        tile_moves = sum(dice_roll)
        logging.debug('%s rolled a %d and %d.' % (player.nickname, dice_roll[0], dice_roll[1]))

        # Whether or not this roll takes us around the board again.
        circular_roll = False

        # If the player's current tile, plus the number of tiles we're moving to (based on our
        # dice roll) is more than the total number of times, we're going around the board passed
        # the GO tile. To get the correct `dest_tile_step` we add the current step plus the tile
        # moves and subtract the total number of times.
        if (player.tile.step + tile_moves) > self.total_tile_count:
            circular_roll = True
            dest_tile_step = (player.tile.step + tile_moves) - self.total_tile_count
        else:
            # If we aren't about to go around the board, the `dest_tile_step` is simply the current
            # tile's step plus the total moves the player has rolled on their dice.
            dest_tile_step = player.tile.step + tile_moves

        # The tiles we've found that the user is going to journey through.
        # These tiles should always be between the player's NEXT tile and
        # up to and including their destination tile.
        journey_tiles = []

        # Iterate over each tile...
        for tile in self.tiles:

            # If our roll takes us over GO...
            if circular_roll:
                # A valid tile is between the player's current tile, and the end of the board,
                # OR, if the tile's step is below the destination tile's step.
                if player.tile.step < tile.step <= self.total_tile_count or tile.step <= dest_tile_step:
                    journey_tiles.append(tile)
            else:
                # If the roll doesn't take us across go, a valid next tile is
                # between the player's current tile and the destination tile.
                if player.tile.step < tile.step <= dest_tile_step:
                    journey_tiles.append(tile)

        # We've now built up a list, `journey_tiles`, of Tiles which the player is going to navigate
        # across. However, if the turn is circular (we're going around the board again), we need to
        # ensure that pre-GO tiles are sorted before post-GO tiles. For example, if I'm at Super Tax
        # (the penultimate tile), I need to navigate across Mayfair first (#40) before I start navigating
        # across GO (#1), Old Kent Road (#2), etc. As we can't simply sort (we need highest step DESC, then
        # highest step ASC), we'll:
        # 1) Pluck out the pre_go_tiles (between player's next tile and the end of the board).
        # 2) Establish what the difference is between the journey tiles and the pre_go_tiles (post_go_tiles).
        # 3) Sort the post_go_tiles by step ASC.
        # 4) Re-create the journey tiles, sticking the pre-GO tiles first.
        if circular_roll:
            pre_go_tiles = [t for t in journey_tiles if t.step > player.tile.step and t.step <= self.total_tile_count]
            post_go_tiles = list(set(journey_tiles) - set(pre_go_tiles))
            post_go_tiles.sort(key=lambda t: t.step)
            journey_tiles = pre_go_tiles + post_go_tiles

        # Iterate over each journey tile...
        for tile in journey_tiles:
            # Have we arrived at our destination?
            if tile.step == dest_tile_step:
                player.handle_land_on_tile(tile)
            else:
                # For each tile, handle what happens when you transit across it.
                player.handle_transit_tile(tile)

        # Did the player roll double die?
        if dice_roll[0] == dice_roll[1]:
            logging.debug('%s rolled a double, they get to roll again.' % player.nickname)
            self.handle_play_turn(player)

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
                    if player.in_jail:
                        self.handle_jail_turn(player)
                    else:
                        self.handle_play_turn(player)
                    sleep(2)
        except KeyboardInterrupt:
            print 'Game has been suspended.'
            sys.exit(0)


class LocaleDoesNotExist(Exception):
    """
    The requested locale does not yet exist.
    """
    pass
