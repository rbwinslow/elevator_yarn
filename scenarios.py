import random

from elevator import Elevator


class Scenario:
    CONTINUE = 0
    COMPLETED = 1
    TIMED_OUT = 2
    STUCK = 3

    def __init__(self):
        self._done = False
        self._max_duration = 60 * 2
        self._min_building_height = 2

    def finished(self):
        self._done = True

    @property
    def max_duration(self):
        return self._max_duration

    @max_duration.setter
    def max_duration(self, value):
        self._max_duration = value

    @property
    def min_building_height(self):
        return self._min_building_height

    @min_building_height.setter
    def min_building_height(self, value):
        self._min_building_height = value

    def should_continue(self, elapsed, building):
        if self._done:
            return self.COMPLETED
        elif elapsed > self.max_duration:
            return self.TIMED_OUT
        else:
            return self.CONTINUE


class OneGuyGoesUp(Scenario):

    def __init__(self, building):
        super().__init__()
        self.max_duration = Elevator.calculate_optimal_trip(0, len(building.floors) - 1) + 2

    def update(self, elapsed, building):
        if elapsed == 0:
            rider = building.new_rider(0, len(building.floors) - 1, elapsed)
            rider.started_waiting = elapsed
            rider.on('reached_destination', lambda _: self.finished())


class TenRandomRides(Scenario):
    RIDE_START_CHANCE_PER_SECOND = 1 / 5

    def __init__(self, building):
        super().__init__()
        self.building_height = len(building.floors)
        self.max_duration = 10 * Elevator.calculate_optimal_trip(0, self.building_height - 1)
        self.riders_finished = 0
        self.riders_started = 0

    def handle_ride_finished(self, _):
        self.riders_finished += 1
        if self.riders_finished == 10:
            self.finished()

    def update(self, elapsed, building):
        if self.riders_started == 10:
            return

        if not self.riders_started or random.random() < self.RIDE_START_CHANCE_PER_SECOND:
            start = end = random.randint(0, self.building_height - 1)
            while end == start:
                end = random.randint(0, self.building_height - 1)
            rider = building.new_rider(start, end, elapsed)
            rider.started_waiting = elapsed
            rider.on('reached_destination', self.handle_ride_finished)
            self.riders_started += 1
