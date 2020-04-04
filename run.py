#!/usr/local/bin/python
import argparse
import importlib
import inspect
import re
import sys
import time

from building import Building
from errors import GameplayError
from scenarios import Scenario

SCENARIO_CLASS_REGEX = re.compile(r'^class (\w+)\(Scenario\):$')


def get_elevator_positions(building):
    return [e.floor_num for e in building.elevators]


def import_scenarios():
    mod = sys.modules['scenarios']
    return {nm:clz for (nm, clz) in
            inspect.getmembers(mod, inspect.isclass) if nm != 'Scenario' and issubclass(clz, Scenario)}


def nope(error):
    print(error)
    exit(1)


def print_conclusion(scenario_conclusion, elapsed):
    print()
    if scenario_conclusion == Scenario.COMPLETED:
        print(f'Scenario concluded successfully at {elapsed} seconds.')
    elif scenario_conclusion == Scenario.TIMED_OUT:
        print(f'Scenario incomplete, but stopped at {elapsed} seconds (maximum duration).')
    elif scenario_conclusion == Scenario.STUCK:
        print(f'Controller seems stuck; stopped at {elapsed} seconds, ten seconds after last elevator movement.')


def print_messages(building):
    if len(building.all_messages) == 0:
        return

    dashes = '-' * building.DRAW_MESSAGES_PREFIX
    print(dashes, 'messages begin', dashes)
    for msg in building.all_messages:
        print(msg)
    print(dashes, 'messages end', dashes)


def simulate(scenario, building, controller, speedup, force_duration=None):
    elapsed = 0
    try:
        elevator_positions = get_elevator_positions(building)
        positions_last_changed = 0
        while True:
            scenario.update(elapsed, building)
            should_continue = scenario.should_continue(elapsed, building)
            if should_continue != Scenario.CONTINUE:
                if should_continue != Scenario.TIMED_OUT or force_duration is None or elapsed >= force_duration:
                    print_conclusion(should_continue, elapsed)
                    break
            elif force_duration is not None and force_duration < elapsed:
                print_conclusion(Scenario.TIMED_OUT, elapsed)
                break
            msg = controller.update(elapsed, building.elevators, building.floors)
            if msg is not None:
                building.add_message('Ctr', elapsed, msg)
            building.update_all(elapsed)
            building.notify_all(elapsed)
            building.draw(elapsed)

            positions_now = get_elevator_positions(building)
            if positions_now != elevator_positions:
                elevator_positions = positions_now
                positions_last_changed = elapsed
            elif positions_last_changed < elapsed - 10:
                print_conclusion(Scenario.STUCK, elapsed)
                break

            time.sleep(1 / speedup)
            elapsed += 1
        print()
        score = building.score(elapsed)
        print(f'SCORE: finished rides                   = {score["finished_rides"]}')
        print(f'       unfinished rides                 = {score["unfinished_rides"]}')
        print(f'       average wait for elevator        = {score["average_wait"]} seconds')
        print(f'       trip efficiency score (1 - 100)  = {score["trip_efficiency"]}')
        print()
        print_messages(building)
    except GameplayError as ge:
        print()
        print(f'GAMEPLAY ERROR: {str(ge)}')
        print_messages(building)
        print()
        raise ge
    except Exception as ex:
        print()
        print('EXCEPTION RAISED!')
        print_messages(building)
        print()
        raise ex


def scenario_pairs_in_source_order(scenarios):
    result = []
    with open('scenarios.py', 'rt') as f:
        while True:
            line = f.readline()
            if not line:
                break
            m = SCENARIO_CLASS_REGEX.match(line.rstrip())
            if m and m[1] in scenarios:
                result.append((m[1], scenarios[m[1]]))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fun elevator game (rip-off of the excellent Elevator Saga)')
    parser.epilog = 'The "controller" argument must be the beginning of the source file name for a controller ' \
                    '("dumb" --> dumb_controller.py). The source file has to contain a class, and the name of the ' \
                    'class has to end with "Controller."'
    parser.add_argument('controller', type=str, nargs=1, help='controller file name prefix (see below)')
    parser.add_argument('--duration', type=int, nargs='?', help='force the game to simulate this many seconds')
    parser.add_argument('--elevators', type=int, default=3, help='number of elevators in building')
    parser.add_argument('--floors', type=int, default=5,
                        help='building height (needs to fit in your terminal window!)')
    parser.add_argument('--list', action='store_true', help='list scenario names and then quit')
    parser.add_argument('--msgwidth', type=int, default=40, help='how wide should the message area be?')
    parser.add_argument('--only', type=str, nargs='?', help='only run these scenarios')
    parser.add_argument('--speedup', type=float, default=4,
                        help='simulation runs this many times faster than real world')
    parser.add_argument('--trace-riders', action='store_true', help='generate debug messages describing rider actions')

    args = parser.parse_args()
    scenarios = import_scenarios()

    if args.list:
        print('\n'.join(scenarios.keys()))
        exit(0)

    modname = f'{args.controller[0]}_controller'
    try:
        mod = importlib.import_module(modname)
        clazz = next(clz for (nm, clz) in inspect.getmembers(mod, inspect.isclass) if nm.endswith('Controller'))
    except ModuleNotFoundError:
        nope(f"It doesn't look like there's a {modname}.py file in this directory.")
    except StopIteration:
        nope(f"Can't find a class that ends with \"Controller\" in {modname}.py.")

    if args.only:
        scenarios = {args.only: scenarios[args.only]}

    scenario_list = scenario_pairs_in_source_order(scenarios)

    for scenario_name, scenario in scenario_list:
        building = Building(elevator_count=args.elevators,
                            floor_count=args.floors,
                            message_width=args.msgwidth,
                            name=scenario_name,
                            trace_riders=args.trace_riders)
        controller = clazz(building.elevators, building.floors)
        scenario = scenario(building)

        simulate(scenario, building, controller, args.speedup,
                 force_duration=(None if args.duration is None else args.duration))
