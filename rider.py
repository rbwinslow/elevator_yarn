from events import EventSource


class Rider(EventSource):

    last_number = 0

    def __init__(self, start, destination):
        super().__init__(('reached_destination',))
        self.destination_floor_num = destination
        self.in_elevator = None
        self.start_floor_num = start
        self.started_waiting = None
        self.trip_end = None
        self.trip_start = None

        Rider.last_number += 1
        self.number = Rider.last_number
