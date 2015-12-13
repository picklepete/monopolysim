import logging


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
        logging.debug('%s has visited "%s".' % (player.nickname, self.name))


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
        player.wallet.deposit(200)
        logging.debug('%s has passed GO and collected 200.' % player.nickname)


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
        player.in_jail = True
        logging.debug('%s has arrived at Go To Jail, they are now in jail.' % player.nickname)


class TaxableTile(Tile):
    """
    A Tile which, when visited, taxes the player.
    """
    def on_land(self, player):
        player.wallet.withdraw(self.tax)
        logging.debug('%s has arrived at "%s", they have been taxed %d.' % (player.nickname, self.name, self.tax))


class PropertyTile(Tile):
    pass
