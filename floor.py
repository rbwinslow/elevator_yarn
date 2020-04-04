import collections

from errors import NoSuchButton
from events import EventSource


class Floor(EventSource):

    def __init__(self, number, has_up_botton=True, has_down_button=True):
        super().__init__(('rider_request',))
        self.number = number
        self._lacking_button = None
        if not has_up_botton:
            self._lacking_button = 'up'
        elif not has_down_button:
            self._lacking_button = 'down'
        self._riders_waiting = []

    def add_waiting_rider(self, rider):
        self._riders_waiting.append(rider)
        if rider.start_floor_num < rider.destination_floor_num:
            self.press_up_button()
        else:
            self.press_down_button()

    def notify_all(self):
        return self.notify_pending()

    def pick_up_riders(self, going_up):
        leaving = [r for r in self._riders_waiting if
                   (going_up and r.start_floor_num < r.destination_floor_num) or
                   (not going_up and r.start_floor_num > r.destination_floor_num)]
        staying = [r for r in self._riders_waiting if
                   (going_up and r.start_floor_num > r.destination_floor_num) or
                   (not going_up and r.start_floor_num < r.destination_floor_num)]
        self._riders_waiting = staying
        return leaving

    def press_up_button(self):
        self._check_button('up')
        self.add_pending_event('rider_request', True)

    def press_down_button(self):
        self._check_button('down')
        self.add_pending_event('rider_request', False)

    @property
    def riders_waiting(self):
        return self._riders_waiting

    def _check_button(self, direction):
        if self._lacking_button == direction:
            raise NoSuchButton(f'floor {self.number} has no {direction} button')
