

class Scenario:

    def max_duration(self):
        return 60 * 2


class OneGuyGoesUp(Scenario):

    def __init__(self, building):
        self._max_duration = len(building.floors) + 1
        building.new_rider(0, len(building.floors) - 1)

    def max_duration(self):
        return self._max_duration

    def update(self, elapsed, building):
        pass
