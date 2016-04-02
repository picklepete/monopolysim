from uuid import uuid4
from random import randint

from tiles import PropertyTile
from conf import INITIAL_PLAYER_CASH


class Player(object):
    """
    Represents a single Player playing the game.

    - `tile` represents this player's current position on the board.
    - `cash` represents this player's cash reserves.
    - `token` represents this player's board token (dog, battleship, etc).
    - `in_jail` represents whether or not this player is in jail.
    - `bankrupt` represents this player is bankrupt and out of the game.
    - `nickname` represents this player's name.
    - `portfolio` represents this player's `PropertyTile` portfolio.
    """
    def __init__(self, *args, **kwargs):
        self.id = uuid4().hex
        self.tile = kwargs.get('tile', None)
        self.board = getattr(self.tile, 'board', None)
        self.cash = kwargs.get('cash', INITIAL_PLAYER_CASH)
        self.token = kwargs.get('token', None)
        self.in_jail = kwargs.get('in_jail', False)
        self.jail_exit_rolls = kwargs.get('jail_exit_rolls', 0)
        self.bankrupt = kwargs.get('bankrupt', False)
        self.nickname = kwargs.get('nickname', 'Anonymous')
        self.portfolio = kwargs.get('portfolio', [])
        self.dice_roll_history = []

    def __repr__(self):
        return '<Player: %s>' % str(self.nickname)

    def handle_jail_entry(self):
        self.in_jail = True
        self.tile = self.board.get_tile_by_name('Jail')

    def handle_jail_exit(self):
        self.in_jail = False
        self.jail_exit_rolls = 0

    def construct_houses(self):
        """
        On any given non-jail turn, a player can decide if they wish to
        purchase houses or hotels for their properties.
        TODO: implement this.
        """
        pass

    def jail_exit_choice(self):
        """
        Based on this player's AI, returns their preferred method of
        leaving jail. The available options are:

        1. Pay a fine of 50 and continue on their next turn
        2. Purchase a "Get Out Of Jail Free" card from another player
        3. Use a "Get Out Of Jail Free" card if they have one
        4. Wait there for three turns, rolling the dice on each turn to try to roll a double.
           If they roll a double on any turn, move out of Jail using this dice roll.

        Until the AI system has been implemented, this method will pick "wait".
        """
        # TODO: implement using the "Get Out Of Jail Free" card when the Cards system has been built.
        return 'wait'

    def handle_land_on_tile(self, tile):
        """
        What happens when our Player
        navigates to and stops on this tile?
        """
        # Mark that we've now moved to this tile.
        self.tile = tile

        # Does the tile do anything when you visit it?
        tile.on_land(self)

        if isinstance(tile, PropertyTile):
            # TODO: implement purchasing tiles.
            pass

    def handle_transit_tile(self, tile):
        """
        What happens when our Player
        navigates past this tile?
        """
        # Does this tile do anything when you transit over it?
        tile.on_transit(self)

    @property
    def wallet(self):
        return PlayerWallet(player=self)

    def roll_die(self):
        return randint(1, 6)

    def _roll_dice(self):
        return self.roll_die(), self.roll_die()

    def roll_dice(self):
        die1, die2 = self._roll_dice()
        self.dice_roll_history.append((die1, die2))
        if len(self.dice_roll_history) == 3:
            hist_roll_matches = 0
            for hist_roll in self.dice_roll_history:
                if hist_roll[0] == hist_roll[1]:
                    hist_roll_matches += 1
            self.dice_roll_history = []
            if not self.in_jail and hist_roll_matches == 3:
                self.handle_jail_entry()
                return None
        return die1, die2


class PlayerWallet(object):
    """
    """
    def __init__(self, player):
        self.player = player

    def withdraw(self, amount):
        self.player.cash -= amount

    def deposit(self, amount):
        self.player.cash += amount
