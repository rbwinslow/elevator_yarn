
class DumbElevatorController:
    """Just tell one elevator to visit every floor, over and over again.
    People will eventually get where they're going."""

    def __init__(self, elevators, floors):
        """The simulation harness, as it's creating me, lets me take a look at the elevator and floor objects that
        it contains. Each is a list, and the floors list is ordered from the bottom floor to the top (floor 1, floor2,
        etc.)."""
        an_elevator = elevators[0]     # Let's use the first elevator
        an_elevator['direction'] = 'up'    # Let's attach some arbitrary datum to it that we'll use later.

        # Whenever the elevator is idle, tell it to go in the direction we think we're going.
        def handle_idle(elevator):
            """Whenever the elevator is idle, tell it to go in the direction we think we're going. If we hit the
            end of the run, then switch directions."""
            if elevator.floor_num == len(floors) - 1 and elevator['direction'] == 'up':
                elevator['direction'] = 'down'
            elif elevator.floor_num == 0 and elevator['direction'] == 'down':
                elevator['direction'] = 'up'

            if elevator['direction'] == 'up':
                elevator.go_up()
            else:
                elevator.go_down()

        # Whenever the elevator reaches a floor, open the doors.
        def handle_arrive_at_floor(elevator, floor):
            elevator.open_doors_and_board_riders(elevator['direction'] == 'up')

        an_elevator.on('idle', handle_idle)
        an_elevator.on('arrive_at_floor', handle_arrive_at_floor)
        an_elevator.open_doors_and_board_riders(an_elevator['direction'] == 'up')

    def update(self, elapsed, elevators, floors):
        """I will call this function periodically. The elapsed value will contain the number of seconds (in the
        simulation) that have passed since the last time I called this update function."""
