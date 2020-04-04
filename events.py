import collections


class EventSource:

    def __init__(self, event_names):
        self._event_names = event_names
        self._handlers = collections.defaultdict(list)
        self._pending_events = []

    def add_pending_event(self, name, *args):
        self._pending_events.append((name, *args))

    def on(self, event_name, handler):
        if event_name not in self._event_names:
            raise ValueError(f'unrecognized event name "{event_name}"')
        self._handlers[event_name].append(handler)

    def notify(self, event_name, *args):
        messages = []
        for f in self._handlers[event_name]:
            m = f(self, *args)
            if m is not None:
                messages.append(m)
        return messages

    def notify_pending(self):
        messages = []
        for e in self._pending_events:
            m = self.notify(*e)
            if m is not None:
                messages.extend(m)
        self._pending_events = []
        return messages
