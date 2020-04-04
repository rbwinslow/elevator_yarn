import collections

from errors import DoorsAreOpen
from events import EventSource


class Elevator(EventSource):

    IDLE = 0
    GOING_UP = 1
    GOING_DOWN = 2
    STOPPED = 3
    OPENING_DOORS_TO_BOARD = 4
    BOARDING_RIDERS = 5
    CLOSING_DOORS = 6
    OPENING_DOORS_TO_DISGORGE = 7
    DISGORGING_RIDERS = 8

    SECONDS_BETWEEN_FLOORS = 4

    def __init__(self, number, starting_floor_num=0):
        self.number = number
        super().__init__(('arrive_at_floor', 'floor_button_pressed', 'idle'))
        self._now_boarding_direction = None
        self._contoller_data = {}
        self._at_floor_num = starting_floor_num
        self._riders = []
        self._status = self.IDLE

    def __contains__(self, item):
        return item in self._contoller_data

    def __delitem__(self, key):
        del self._contoller_data[key]

    def __getitem__(self, key):
        return self._contoller_data[key]

    def __setitem__(self, key, value):
        self._contoller_data[key] = value

    @property
    def floor_num(self):
        return self._at_floor_num

    @property
    def rider_count(self):
        return len(self._riders)

    @property
    def status(self):
        return self._status

    def open_doors_and_board_riders(self, going_up):
        """Stop the elevator, open its doors (letting riders on and off) and then close its doors.
        The whole operation wil take three game seconds, and at the end, the elevator will be idle."""
        self._status = self.OPENING_DOORS_TO_BOARD
        self._now_boarding_direction = 'up' if going_up else 'down'

    def open_doors_to_disembark(self):
        self._status = self.OPENING_DOORS_TO_DISGORGE

    @classmethod
    def calculate_optimal_trip(cls, start, destination):
        dist = abs(destination - start)
        # 3 seconds for all doors/embarkation time
        return dist * cls.SECONDS_BETWEEN_FLOORS + 3

    def go_down(self):
        if self._status != self.IDLE:
            raise DoorsAreOpen()
        self._status = self.GOING_DOWN

    def go_up(self):
        if self._status != self.IDLE:
            raise DoorsAreOpen()
        self._status = self.GOING_UP

    def notify_all(self):
        messages = self.notify_pending()
        if self._status == self.IDLE:
            msg = self.notify('idle')
            if len(msg) > 0:
                messages.extend(msg)
        return messages

    def riders_boarded(self, riders):
        self._riders.extend(riders)
        for r in riders:
            self.add_pending_event('floor_button_pressed', r.destination_floor_num)

    def update(self, elapsed, building):
        was_at_floor_num = self._at_floor_num
        floor_increment = 1 / self.SECONDS_BETWEEN_FLOORS
        if self._status == self.GOING_UP:
            if self._at_floor_num < len(building.floors) - 1:
                self._at_floor_num += floor_increment
            else:
                self._status = self.IDLE
        elif self._status == self.GOING_DOWN:
            if self._at_floor_num > 0:
                self._at_floor_num -= floor_increment
            else:
                self._status = self.IDLE
        elif self._status == self.OPENING_DOORS_TO_BOARD:
            self._status = self.BOARDING_RIDERS
        elif self._status == self.BOARDING_RIDERS:
            building.elevator_take_in_riders(self, self._now_boarding_direction == 'up', elapsed)
            self._disgorge_riders(building, elapsed)
            self._now_boarding_direction = None
            self._status = self.CLOSING_DOORS
        elif self._status == self.CLOSING_DOORS:
            self._status = self.IDLE
        elif self._status == self.OPENING_DOORS_TO_DISGORGE:
            self._status == self.DISGORGING_RIDERS
        elif self._status == self.DISGORGING_RIDERS:
            self._disgorge_riders(building, elapsed)
            self._status = self.CLOSING_DOORS

        # In case floating-point math screws me up…
        if abs(round(self._at_floor_num) - self._at_floor_num) < 0.01:
            self._at_floor_num = round(self._at_floor_num)

        if was_at_floor_num != self._at_floor_num and isinstance(self._at_floor_num, int):
            self._pending_events.append(('arrive_at_floor', building.floors[self._at_floor_num]))

    def _disgorge_riders(self, building, elapsed):
        leaving = [r for r in self._riders if r.destination_floor_num == self._at_floor_num]
        staying = [r for r in self._riders if r.destination_floor_num != self._at_floor_num]
        if len(leaving) > 0:
            building.elevator_expel_riders(leaving, elapsed)
        self._riders = staying
