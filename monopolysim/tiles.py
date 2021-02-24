import logging

from conf import GO_TRANSIT_PAYMENT


class Tile(object):
    """
    Our base Tile object.
    """
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Tile: %s (%s)>' % (self.name, self.type.capitalize())

    def on_land(self, player):
        """
        What happens when our Player
        navigates to and stops on this tile?
        """
        logging.debug('%s has arrived at "%s".' % (player.nickname, self.name))

    def on_transit(self, player):
        """
        What happens when our Player
        navigates past this tile?
        """
        logging.debug('\t%s has visited "%s".' % (player.nickname, self.name))


class NoopTile(Tile):
    """
    A Tile where nothing happens on a visit or transit.
    """
    pass


class CardTile(Tile):
    """
    Our base CardTile object.
    """
    pass


class ChanceTile(CardTile):
    """
    """
    pass


class CommunityChestTile(CardTile):
    """
    """
    pass


class GoTile(Tile):
    """
    The corner "GO" tile.
    """
    def on_transit(self, player):
        player.wallet.deposit(GO_TRANSIT_PAYMENT)
        logging.debug('%s has passed GO and collected %d.' % (player.nickname, GO_TRANSIT_PAYMENT))


class FreeParkingTile(NoopTile):
    """
    The corner "Free Parking" tile.
    """
    pass


class JailTile(NoopTile):
    """
    The corner "Jail" tile.
    """
    pass


class GoToJailTile(Tile):
    """
    The corner "Go To Jail" tile.
    """
    def on_land(self, player):
        player.handle_jail_entry()
        logging.debug('%s has arrived at Go To Jail, they are now in jail.' % player.nickname)


class TaxableTile(Tile):
    """
    A Tile which, when visited, taxes the player.
    """
    def on_land(self, player):
        player.wallet.withdraw(self.tax)
        logging.debug('%s has arrived at "%s", they have been taxed %d.' % (player.nickname, self.name, self.tax))


class PropertyTile(Tile):
    """
    All purchasable tiles are of this tile type.
    """
    def __init__(self, *args, **kwargs):
        super(PropertyTile, self).__init__(*args, **kwargs)
        self.owner = None
        self.houses = 0
        self.hotel = False

    @property
    def is_owned(self):
        return self.owner is not None

    def get_upgrade_price(self):
        """
        """
        if not self.hotel and self.houses == 4:
            return 'hotel', self.prices['hotel']
        return 'house', self.prices['house']

    def get_rent_cost(self, dice_roll):
        """
        When you land on a property, the number of houses decides
        how much the rent is. When you load on a station, the number
        of stations owned by the same player decides the price. When
        you land on a utility, if one is owned, the rent is four times
        the dice roll. If both utilities are owned, rent is ten times
        the dice roll.
        """
        if self.type == 'property':
            houses = str(self.houses)
            if self.hotel:
                houses = '5'
            return self.prices['rent'][houses]
        elif self.type == 'station':
            owner_portfolio = self.owner.get_portfolio()
            owner_total_stations = len(owner_portfolio['station'])
            return self.prices['rent'][str(owner_total_stations)]
        elif self.type == 'utility':
            owner_portfolio = self.owner.get_portfolio()
            owner_total_utilities = len(owner_portfolio['utility'])
            if owner_total_utilities == 1:
                return sum(dice_roll) * 4
            elif owner_total_utilities == 2:
                return sum(dice_roll) * 10
            raise ValueError('Unexpectedly found %d utility tiles, expected one or two.' % owner_total_utilities)
