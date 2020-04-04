

class GameplayError(Exception):
    """Errors the controller might make that break the game."""

class DoorsAreOpen(GameplayError):
    def __init__(self):
        super().__init__('Tried to move an elevator up or down while its doors are open.')

class NoSuchButton(Exception):
    pass
