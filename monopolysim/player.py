import logging
from uuid import uuid4
from random import randint
from collections import defaultdict

import conf
from tiles import PropertyTile


class Player(object):
    """
    Represents a single Player playing the game.

    - `tile` represents this player's current position on the board.
    - `portfolio` represents this player's tile portfolio.
    - `cash` represents this player's cash reserves.
    - `token` represents this player's board token (dog, battleship, etc).
    - `in_jail` represents whether or not this player is in jail.
    - `bankrupt` represents this player is bankrupt and out of the game.
    - `nickname` represents this player's name.
    """
    def __init__(self, *args, **kwargs):
        self.id = uuid4().hex
        self.portfolio = []
        self.tile = kwargs.get('tile', None)
        self.board = getattr(self.tile, 'board', None)
        self.cash = kwargs.get('cash', conf.INITIAL_PLAYER_CASH)
        self.token = kwargs.get('token', None)
        self.in_jail = kwargs.get('in_jail', False)
        self.jail_exit_rolls = kwargs.get('jail_exit_rolls', 0)
        self.bankrupt = kwargs.get('bankrupt', False)
        self.nickname = kwargs.get('nickname', 'Anonymous')
        self.dice_roll_history = []

    def __repr__(self):
        return '<Player: %s>' % str(self.nickname)

    def handle_jail_entry(self):
        self.in_jail = True
        self.tile = self.board.get_tile_by_name('Jail')

    def handle_jail_exit(self):
        self.in_jail = False
        self.jail_exit_rolls = 0

    def get_portfolio(self):
        """
        Returns the player's property portfolio, grouped by `type`.
        """
        portfolio = defaultdict(list)
        tiles = filter(lambda t: t.type in ['property', 'station', 'utility'], self.board.tiles)
        for tile in tiles:
            if tile.owner == self:
                group_by = 'group'
                if tile.type in ['station', 'utility']:
                    group_by = 'type'
                portfolio[getattr(tile, group_by)].append(tile)
        return portfolio

    def construct_houses(self):
        """
        On any given non-jail turn, a player can decide if they wish to
        purchase houses or hotels for their properties.
        TODO: implement this.
        """
        pass

    def property_purchase_choice(self, purchase_price):
        """
        What should the Player do when given the option to purchase?
        By default, if they have the cash, they'll purchase it.
        """
        return conf.PLAYER_PURCHASE_PROPERTY

    def property_build_choice(self, upgrade_price):
        """
        What should the Player do when given the option to upgrade?
        By default, if they have the cash, they'll upgrade.
        """
        return conf.PLAYER_BUILD_PROPERTY

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
        return conf.PLAYER_JAIL_WAIT

    def pay_rent(self, tile, price):
        """
        Handles rent payment between the property owner and this player.
        """
        self.wallet.withdraw(price)
        tile.owner.wallet.deposit(price)
        logging.debug('%s paid %s %d in rent.' % (self.nickname, tile.owner.nickname, price))

    def purchase_property(self, tile):
        """
        Handles purchasing a new property.
        """
        tile.owner = self
        price = tile.prices['purchase']
        self.portfolio.append(tile)
        self.wallet.withdraw(price)
        logging.debug('%s has purchased "%s".' % (self.nickname, tile.name))

    def upgrade_property(self, tile):
        """
        Handles upgrading an existing property.
        """
        upgrade_type, upgrade_price = tile.get_upgrade_price()
        if upgrade_type == 'hotel':
            tile.hotel = True
            logging.debug('%s upgraded "%s" to a hotel.' % (self.nickname, tile.name))
        else:
            tile.houses += 1
            logging.debug('%s has added a house to "%s", the total is now %d.' % (
                self.nickname,
                tile.name,
                tile.houses
            ))
        self.wallet.withdraw(upgrade_price)

    def handle_land_on_tile(self, tile, dice_roll):
        """
        What happens when our Player
        navigates to and stops on this tile?
        """
        # Mark that we've now moved to this tile.
        self.tile = tile

        # Does the tile do anything when you visit it?
        tile.on_land(self)

        # If this tile is a property, does the player have
        # rent to pay if it's owned? If it's not owned, does
        # the player want to buy it?
        if isinstance(tile, PropertyTile):
            if not tile.is_owned:
                price = tile.prices['purchase']
                if self.cash >= price:
                    decision = self.property_purchase_choice(price)
                    if decision == conf.PLAYER_PURCHASE_PROPERTY:
                        # Purchase the property.
                        self.purchase_property(tile)
                    else:
                        # Player can afford it, but chose not to.
                        logging.debug('%s chose not to buy "%s".' % (self.nickname, tile.name))
                else:
                    # Player can't afford it.
                    logging.debug('%s cannot afford to buy "%s".' % (self.nickname, tile.name))
            elif tile.owner.id == self.id and tile.type == 'property':
                # Only properties, not stations or utilities, can be upgraded.
                # This property belongs to this player.
                # Work out what the upgrade type and cost is.
                upgrade_type, upgrade_price = tile.get_upgrade_price()

                # If the player has enough cash...
                if self.cash >= upgrade_price:
                    # Let the player decide if they want to upgrade.
                    decision = self.property_build_choice(upgrade_price)
                    if decision == conf.PLAYER_BUILD_PROPERTY:
                        # We've chosen to upgrade.
                        self.upgrade_property(tile)
                    else:
                        # Player can afford the upgrade, but chose not to.
                        logging.debug('%s chose not to upgrade "%s".' % (self.nickname, tile.name))
                else:
                    # Player can't afford the upgrade.
                    logging.debug('%s cannot afford to upgrade "%s".' % (self.nickname, tile.name))
            else:
                # This property belongs to someone else.
                rent_price = tile.get_rent_cost(dice_roll)
                # If the player has enough cash...
                if self.cash >= rent_price:
                    # Exchange the rent price.
                    self.pay_rent(tile, rent_price)
                else:
                    # TODO: the player can't afford to pay rent.
                    # Once mortgaging has been built, call it here.
                    self.bankrupt = True
                    logging.debug('%s cannot afford to pay %s rent, they '
                                  'are bankrupt.' % (self.nickname, tile.owner.nickname))

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
    Represents a Player's wallet. Used to have an easy
    interface for withdrawing and depositing cash.
    """
    def __init__(self, player):
        self.player = player

    def withdraw(self, amount):
        if (self.player.cash - amount) <= 0:
            self.player.cash = 0
            self.player.bankrupt = True
            logging.debug('%s is bankrupt.' % self.player.nickname)
        else:
            self.player.cash -= amount

    def deposit(self, amount):
        self.player.cash += amount
