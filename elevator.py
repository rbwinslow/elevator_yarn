from errors import BlownTransmission


class Elevator:

    IDLE = 0
    GOING_UP = 1
    GOING_DOWN = 2
    STOPPED = 3
    BOARDING_RIDERS = 4

    SECONDS_BETWEEN_FLOORS = 4

    def __init__(self, starting_floor=0):
        self._contoller_data = {}
        self._on_floor = starting_floor
        self._status = self.IDLE

    def __getitem__(self, key):
        return self._contoller_data[key]

    def __setitem__(self, key, value):
        self._contoller_data[key] = value

    def __delitem__(self, key):
        del self._contoller_data[key]

    def count_riders(self):
        return 0

    def go_down(self):
        if self._status == self.GOING_UP:
            raise BlownTransmission()
        self._status = self.GOING_DOWN

    def go_up(self):
        if self._status == self.GOING_DOWN:
            raise BlownTransmission()
        self._status = self.GOING_UP

    def on(self, event_name, function):
        pass

    def update(self, elapsed, building):
        floor_increment = 1 / self.SECONDS_BETWEEN_FLOORS
        if self._status == self.GOING_UP:
            if self._on_floor < len(building.floors) - 1:
                self._on_floor += floor_increment
            else:
                self._status = self.IDLE
        elif self._status == self.GOING_DOWN:
            if self._on_floor > 0:
                self._on_floor -= floor_increment
            else:
                self._status = self.IDLE

    @property
    def floor(self):
        return self._on_floor

    @property
    def status(self):
        return self._status
