import math

import collections

from elevator import Elevator
from floor import Floor


class Building:

    DRAW_LEFT_MARGIN_WIDTH = len('FLOOR ##  ')
    DRAW_MAX_ELEVATOR_WIDTH = 5
    DRAW_RIGHT_MARGIN_WIDTH = len('Waiting')

    RIDER_WAITING = 0

    def __init__(self, elevator_count=1, floor_count=2):
        # public interface
        self.elevators = [Elevator() for _ in range(elevator_count)]
        self.floors = [Floor(n) for n in range(floor_count)]
        # internals
        self._riders = list()

    def draw(self, elapsed, name="Building"):
        elevators_width = (self.DRAW_MAX_ELEVATOR_WIDTH + 5) * len(self.elevators)
        total_width = self.DRAW_LEFT_MARGIN_WIDTH + elevators_width + self.DRAW_RIGHT_MARGIN_WIDTH
        height = 2 * len(self.floors) + 2

        if elapsed > 0:
            # redraw (move cursor back up to top-left corner of building)
            print('\033[F' + ('\033[A' * (height - 1)), end='')

        waiting_riders = self._riders_waiting_on_floors()

        self._draw_marquee(name, total_width)
        self._draw_elevator_headings(self.DRAW_LEFT_MARGIN_WIDTH)

        for floor in reversed(self.floors):
            self._draw_floor(floor.number, len(waiting_riders[floor.number]))
            if floor.number > 0:
                # space in between floors, where elevator is shown in transit
                self._draw_floor(floor.number - 0.5, 0)

        self._draw_marquee(f'{elapsed} seconds', total_width)

    def new_rider(self, start_floor, destination_floor):
        if start_floor < 0 or destination_floor >= len(self.floors):
            raise ValueError(f'scenario wanted ride between floors {start_floor} and {destination_floor}; '
                             f'building is {len(self.floors)} tall')
        self._riders.append({'start': start_floor, 'end': destination_floor, 'status': self.RIDER_WAITING})

    def _draw_elevator(self, elevator, for_floor):
        if elevator.on_floor == for_floor:
            elev = f'{{{max(" ", "*" * min(elevator.count_riders(), 3))}}}'.center(self.DRAW_MAX_ELEVATOR_WIDTH)
            print(f'| {elev} | ', end='')
        else:
            print(f'| {" " * self.DRAW_MAX_ELEVATOR_WIDTH} | ', end='')

    def _draw_elevator_headings(self, left_margin):
        headings = '|' + \
                   '| |'.join([f'Elv {n + 1}'.center(self.DRAW_MAX_ELEVATOR_WIDTH + 2) for n in range(len(self.elevators))]) + \
                   '| Waiting'
        print(' ' * left_margin + headings)

    def _draw_floor(self, floor_number, how_many_waiting):
        if int(floor_number) == floor_number:
            print(f'FLOOR {str(floor_number + 1).rjust(2)}  ', end='')
        else:
            print(' ' * self.DRAW_LEFT_MARGIN_WIDTH, end='')

        for elevator in self.elevators:
            self._draw_elevator(elevator, floor_number)

        print('*' * how_many_waiting)

    def _draw_marquee(self, marquee, total_width):
        left_slug_len = int((total_width - len(marquee) - 2) / 2)
        print('=' * left_slug_len, end='')
        print(f' {marquee} ', end='')
        print('=' * (total_width - left_slug_len - len(marquee) - 2))

    def _riders_waiting_on_floors(self):
        result = collections.defaultdict(list)
        for rider in filter(lambda r: r['status'] == self.RIDER_WAITING, self._riders):
            result[rider['start']].append(rider)
        return result
