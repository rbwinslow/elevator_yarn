import math
import statistics

from elevator import Elevator
from floor import Floor
from rider import Rider


class Building:

    DRAW_LEFT_MARGIN_WIDTH = len('FLOOR ##  ')
    DRAW_MAX_ELEVATOR_WIDTH = 5
    DRAW_MESSAGES_PREFIX = len('001 EV1 ')
    DRAW_WAITING_RIDERS_WIDTH = 10

    RIDER_WAITING = 0

    def __init__(self, elevator_count, floor_count, message_width, name='Building', trace_riders=False):
        self.elevators = [Elevator(n) for n in range(elevator_count)]
        self.floors = [Floor(0, has_down_button=False)]
        self.floors.extend(Floor(n) for n in range(floor_count)[1:-1])
        self.floors.append(Floor(floor_count - 1, has_up_botton=False))
        self._all_riders = []
        self._message_width = message_width
        self._messages = []
        self._name = name
        self._trace_riders = trace_riders

    @property
    def all_messages(self):
        return self._messages

    def add_message(self, origin, elapsed, msg):
        assert len(origin) <= 3
        self._messages.append(f'{str(elapsed).rjust(3)} {origin.ljust(3)} {msg}'[:self._message_width])

    def draw(self, elapsed):
        elevators_width = (self.DRAW_MAX_ELEVATOR_WIDTH + 5) * len(self.elevators)
        total_width = self.DRAW_LEFT_MARGIN_WIDTH + elevators_width + self.DRAW_WAITING_RIDERS_WIDTH
        height = 2 * len(self.floors) + 2

        if elapsed > 0:
            # redraw (move cursor back up to top-left corner of building)
            print('\033[F' + ('\033[A' * (height - 1)), end='')

        self._draw_marquee(self._name, total_width)
        self._draw_elevator_headings(self.DRAW_LEFT_MARGIN_WIDTH)

        for floor in reversed(self.floors):
            self._draw_floor(floor.number, len(floor.riders_waiting))
            if floor.number > 0:
                # space in between floors, where elevator is shown in transit
                self._draw_floor(floor.number - 0.5, 0)

        self._draw_marquee(f'{elapsed} seconds', total_width)

    def elevator_expel_riders(self, riders, elapsed):
        assert len(riders) > 0
        for r in riders:
            r.add_pending_event('reached_destination')
            r.trip_end = elapsed
        if self._trace_riders:
            numbers = 'R' + ',R'.join(str(r.number) for r in riders)
            self.add_message('RDR', elapsed,
                             f'riders {numbers} disembarking on floor {riders[0].destination_floor_num}')

    def elevator_take_in_riders(self, elevator, going_up, elapsed):
        boarding = self.floors[elevator.floor_num].pick_up_riders(going_up)
        if len(boarding) == 0:
            return
        for r in boarding:
            r.trip_start = elapsed
        elevator.riders_boarded(boarding)
        if self._trace_riders:
            numbers = 'R' + ',R'.join(str(r.number) for r in boarding)
            self.add_message('RDR', elapsed,
                             f'riders {numbers} boarding Ev{elevator.number} on floor {elevator.floor_num}')

    def new_rider(self, start_floor_num, destination_floor_num, elapsed):
        if not (0 <= start_floor_num < len(self.floors) and 0 <= destination_floor_num < len(self.floors)):
            raise ValueError(f'scenario wanted ride between floors {start_floor_num} and {destination_floor_num}; '
                             f'building is {len(self.floors)} tall')
        if start_floor_num == destination_floor_num:
            raise ValueError(f'scenario wanted ride from floor {start_floor_num} to itself')
        rider = Rider(start_floor_num, destination_floor_num)
        self._all_riders.append(rider)
        self.floors[start_floor_num].add_waiting_rider(rider)
        if self._trace_riders:
            self.add_message(
                'RDR',
                elapsed,
                f'new rider R{rider.number} wants to go from {start_floor_num} to {destination_floor_num}'
            )
        return rider

    def notify_all(self, elapsed):
        for f in self.floors:
            msgs = f.notify_all()
            for m in msgs:
                self.add_message(f'F{f.number}', elapsed, m)
        for i, e in enumerate(self.elevators):
            msgs = e.notify_all()
            for m in msgs:
                self.add_message(f'Ev{i}', elapsed, m)

    def score(self, total_elapsed):
        waits = []
        for r in self._all_riders:
            waits.append((total_elapsed if r.trip_start is None else r.trip_start) - r.started_waiting)

        trip_efficiencies = []
        satisfied = [r for r in self._all_riders if r.trip_end is not None]
        trip_distances = [abs(r.start_floor_num - r.destination_floor_num) for r in satisfied]
        sum_of_distances = sum(trip_distances)
        for i, r in enumerate(satisfied):
            optimal = Elevator.calculate_optimal_trip(r.start_floor_num, r.destination_floor_num)
            base_efficiency = optimal / (r.trip_end - r.trip_start)
            trip_efficiencies.append(base_efficiency * trip_distances[i] / sum_of_distances)

        if len(trip_efficiencies) == 0:
            mean_trip_efficiency = 0
        else:
            mean_trip_efficiency = statistics.mean(trip_efficiencies)

        return {
            'finished_rides': len(satisfied),
            'unfinished_rides': len([r for r in self._all_riders if r.trip_end is None]),
            'average_wait': statistics.mean(waits),
            'trip_efficiency': round(mean_trip_efficiency * 100),
        }

    def update_all(self, elapsed):
        for e in self.elevators:
            e.update(elapsed, self)
        for r in self._all_riders:
            r.notify_pending()

    def _draw_elevator(self, elevator, for_floor_num):
        if isinstance(for_floor_num, int):
            draw_it = (elevator.floor_num == for_floor_num)
        else:
            draw_it = math.floor(for_floor_num) < elevator.floor_num < math.ceil(for_floor_num)

        if draw_it:
            open_door_states = (elevator.OPENING_DOORS_TO_BOARD, elevator.OPENING_DOORS_TO_DISGORGE,
                                elevator.BOARDING_RIDERS, elevator.DISGORGING_RIDERS)
            if elevator.status in open_door_states:
                elev = f'<{max(" ", "*" * min(elevator.rider_count, 3))}>'.center(self.DRAW_MAX_ELEVATOR_WIDTH)
            elif elevator.status == elevator.CLOSING_DOORS:
                elev = f'>{max(" ", "*" * min(elevator.rider_count, 3))}<'.center(self.DRAW_MAX_ELEVATOR_WIDTH)
            else:
                elev = f'{{{max(" ", "*" * min(elevator.rider_count, 3))}}}'.center(self.DRAW_MAX_ELEVATOR_WIDTH)
            print(f'| {elev} | ', end='')
        else:
            print(f'| {" " * self.DRAW_MAX_ELEVATOR_WIDTH} | ', end='')

    def _draw_elevator_headings(self, left_margin):
        headings = '|' + \
                   '| |'.join([f'Elv {n}'.center(self.DRAW_MAX_ELEVATOR_WIDTH + 2) for n in range(len(self.elevators))]) + \
                   '| Waiting'
        print(' ' * left_margin + headings)

    def _draw_floor(self, floor_number, how_many_waiting):
        if int(floor_number) == floor_number:
            print(f'FLOOR {str(floor_number).rjust(2)}  ', end='')
        else:
            print(' ' * self.DRAW_LEFT_MARGIN_WIDTH, end='')

        for elevator in self.elevators:
            self._draw_elevator(elevator, floor_number)

        print(('*' * how_many_waiting).ljust(self.DRAW_WAITING_RIDERS_WIDTH, ' '), end='')

        if len(self._messages) > floor_number * 2:
            msg = self._messages[-(round(floor_number * 2) + 1)]
            print(msg.ljust(self._message_width + self.DRAW_MESSAGES_PREFIX, ' '))
        else:
            print(' ' * self._message_width)

    def _draw_marquee(self, marquee, total_width):
        left_slug_len = int((total_width - len(marquee) - 2) / 2)
        print('=' * left_slug_len, end='')
        print(f' {marquee} ', end='')
        print('=' * (total_width - left_slug_len - len(marquee) - 2))
