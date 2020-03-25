
class DumbElevatorController:
    """Just tell one elevator to visit every floor, over and over again.
    People will eventually get where they're going."""

    def __init__(self, elevators, floors):
        """The simulation harness, as it's creating me, lets me take a look at the elevator and floor objects that
        it contains. Each is a list, and the floors list is ordered from the bottom floor to the top (floor 1, floor2,
        etc.)."""
        an_elevator = elevators[0]     # Let's use the first elevator

        # Whenever the elevator is idle (has no more queued destinations), tell it to go visit every floor:
        def handle_idle(elevator):
            if elevator.floor.number == 0:
                elevator.go_up()
            # for n in range(len(floors)):
            #     elevator.goToFloor(n)

        an_elevator.on("idle", handle_idle)

    def update(self, elapsed, elevators, floors):
        """I will call this function periodically. The elapsed value will contain the number of seconds (in the
        simulation) that have passed since the last time I called this update function."""
