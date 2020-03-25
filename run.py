#!/usr/local/bin/python
import argparse
import importlib
import inspect
import sys
import textwrap
import time

from building import Building
from scenarios import OneGuyGoesUp


def nope(error):
    print(error)
    exit(1)


def simulate(building, controller, speedup=4):
    scenario = OneGuyGoesUp(building)
    for elapsed in range(scenario.max_duration()):
        scenario.update(elapsed, building)
        controller.update(elapsed, building.elevators, building.floors)
        building.draw(elapsed)
        time.sleep(1 / speedup)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fun elevator game (rip-off of the excellent Elevator Saga)')
    parser.epilog = 'The "controller" argument must correspond to the name of a controller source file ' \
                    '("dumb" --> dumb_controller.py). The source file has to contain a class, and the name of the ' \
                    'class has to end with "Controller."'
    parser.add_argument('controller', type=str, nargs=1, help='part of controller source file name before "_controller.py"')
    parser.add_argument('--only', type=str, nargs='*', help='only run this scenario')

    args = parser.parse_args()
    modname = f'{args.controller[0]}_controller'
    try:
        mod = importlib.import_module(modname)
        clazz = next(clz for (nm, clz) in inspect.getmembers(mod, inspect.isclass) if nm.endswith('Controller'))
    except ModuleNotFoundError:
        nope(f"It doesn't look like there's a {modname}.py file in this directory.")
    except StopIteration:
        nope(f"Can't find a class that ends with \"Controller\" in {modname}.py.")

    building = Building(elevator_count=2)
    controller = clazz(building.elevators, building.floors)

    simulate(building, controller)
