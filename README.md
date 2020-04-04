# Elevator Yarn

Like Elevator Saga, but _much dumber_.

The simulation environment is more simplistic than that in Elevator Saga, and
it requires more work on the part of the player (the controller class) to
directly control the movement and other behavior of elevators (and planning
for same). In Elevator Yarn, you don't get to have an elevator conveniently
enqueue and execute a journey to the fifth floor; you have to tell it to start
going up, and tell it to stop and open its doors when it gets there. This is
intentional, as Elevator Yarn is intended as a little more of a programming
exercise, as much as it is a game.

## Try it out

You should run Elevator Yarn using Python 3.6 or later. The program doesn't
depend on any packages aside from those included with Python.

The basic structure of the simulation command is this:

```
$ ./run.py [options] controller_name
```

`controller_name` is the first part of the name of a controller source file
that you've written and that you want to test with the simulation. There's an
example `DumbController` that's not very good at its job, but can be used to
demonstrate the simulation. It's implemented in the source file
"dump_controller.py," so you would use just the name "dumb" as your
`controller_name` argument on the command line, like this:

```
$ ./run.py --only OneGuyGoesUp dumb
====== OneGuyGoesUp =======
          | Elv 1 | Waiting
FLOOR  5  |       |
          |       |
FLOOR  4  |  <*>  |
          |       |
FLOOR  3  |       |
          |       |
FLOOR  2  |       |
          |       |
FLOOR  1  |       |
======= 20 seconds ========

Scenario incomplete, but stopped at 21 seconds (maximum duration).

SCORE: finished rides            = 0
       unfinished rides          = 1
       average wait for elevator = 1 seconds
       average trip inefficiency = 99
```

The `OneGuyGoesUp` scenario is hyper-simple: there's only one rider, who
presses the up button on the ground floor, wanting to go up to the top
floor. When that one trip is finished, the simulation ends. Note how the
`--only` flag is used to run only that one scenario.

Note, however, the "Scenario incomplete" conclusion. `DumbController` is
actually so dumb that if you test it with even the simplest scenario (see "How
the game runs and scores", below), it takes too long to finish and gets cut
off by the simulation. That's because the controller makes the simulated
elevator stop at every single floor it passes, and the scenario expects the
whole trip to be finished sooner.

You can use the `--duration` argument on the command line to force the
simulation to run longer, allowing the elevator to finish this one scenario:

```
$ ./run.py --only OneGuyGoesUp --duration 30 dumb
====== OneGuyGoesUp =======
          | Elv 1 | Waiting
FLOOR  5  |  > <  |
          |       |
FLOOR  4  |       |
          |       |
FLOOR  3  |       |
          |       |
FLOOR  2  |       |
          |       |
FLOOR  1  |       |
======= 29 seconds ========

Scenario concluded successfully at 30 seconds.

SCORE: finished rides            = 1
       unfinished rides          = 0
       average wait for elevator = 1 seconds
       average trip efficiency   = 0.75
```

The "average trip efficiency" value is a very rough attempt at quantifying how
quickly trips were completed versus their "optimal" (minimal) timing.

There are other command-line options that allow you to change simulation
parameters like the height of the building and the number of elevators. Run
`./run.py -h` to see them all.

## How to play

You're writing an elevator controller. It controls what the elevators do in a
simulated building, with simulated people in it. You write a controller class
(its name has to end in "Controller"), and you name the source file it's in so
that its name ends with "_controller.py"

Your class needs to have two functions, `__init__` and `update`, and they look
like this:

```python
class MyController:
    def __init__(self, elevators, floors):
        pass

    def update(self, elapsed, elevators, floors):
        pass
```

The`__init__` function is called once, before the simulation starts running,
so that the controller can initialize itself and set up any event handlers it
needs on elevators and floors (more about this later).

The `update` function is called once every "second" in the simulated game
world. The `update` function gets told how many seconds have passed since the
beginning of the simulation, in case it's interested, and gets another crack
at the elevators and floors.

What are these elevators and floors? They're lists of objects – a list of
elevator objects and a list of floor objects. Each elevator object represents
one of the elevators in the building, and it knows things about itself (what
direction it's moving, what riders are inside it), but it doesn't know _what
to do_ about it. You have to tell it which direction to go, when to stop and
open doors … stuff like that.

Floor objects also know stuff about themselves, like when people press the up
or down button to call for an elevator on that floor, or what people are
waiting and where they want to go.

The Elevator and Floor objects in a building don't change over time. If you
want to squirrel away either list of objects for use in an event handler, for
example, feel free to do it like this...

```python
class MyController:
    def __init__(self, elevators, floors):
        self.the_elevators = elevators
        self.the_floors = floors
```

There's a DumbController class, in dumb_controller.py, to serve as an example.

### Handling events

The two ways your controller class interacts with the simulated world are by
_handling events_ and _calling methods_. The objects representing elevators
and floors in the simulation "know" when certain significant events are
happening to them, such as an elevator reaching a floor or a rider pressing a
button, and you can set yourself up to have a function of your own called
whenever such an event happens to one of these objects, like this:

```python
def handle_arrive_at_floor(elevator, floor):
    # Maybe I want to do something when I reach a floor...

some_elevator.on("arrive_at_floor", handle_arrive_at_floor)
```

Notice how the handler function in this case takes two arguments, an elevator
and a floor. All event handlers are passed at least one argument, and that
first argument is the object whose event you're intercepting itself. So if
you intercept an elevator event like this, the first argument to your handler
function is going to be the elevator object that produced the event.

Some events also pass additional arguments to their handlers, and in this
case, the "arrive_at_floor" event passes along an actual floor object
representing the floor the elevator is arriving at.

Here are the events that elevators allow you to intercept, along with the
arguments that their handler functions should expect:
- arrive_at_floor (elevator, floor)
- floor_button_pressed (elevator, floor_num)
- idle (elevator)

The `arrive_at_floor` event is fired when a rider inside the elevator presses
a number button representing the floor that the rider wants to go to. The
`floor_num` argument is that floor number.

The `idle` event is fired every second that an elevator is idle, which is
to say that it's neither moving nor boarding passengers.

And here's the same list, but for floor objects:
- rider_request (floor, going_up)

The `rider_request` event is fired when a simulated person presses the up or
down elevator call button on a given floor. That "going_up" value is a bool,
signifying whether the up or the down button was pressed.

### Making things happen

Elevator object have methods you can call to make them do things in the
simulated world. You can tell an elevator to start going up or down, and you
can tell it to open its doors for riders to get on and off. You can call
these methods either inside event handler functions like the one illustrated
above, or you can call them from your controller's `update()` function.

Elevators also have a couple of useful properties:

- _floor_num_ - The zero-based index of the floor that the elevator is
    currently on (zero is the ground floor). _Note_ that this can be a
    fraction, as the elevator takes multiple seconds to pass from floor to
    floor.
- _rider_count_ - The number of riders currently riding in this elevator.
- _status_ – A value representing what the elevator is currently doing (one
    of the all-capitals-and-underscores constants defined in the `Elevator`
    class, e.g., Elevator.IDLE, Elevator.GOING_UP).

When you call an elevator's `go_up()` method, the elevator starts going up
and keeps going until you tell it to do something else, or it reaches the top
floor of the building and stops automatically. `go_down()` is an exercise left
for the reader.

The `open_doors_and_board_riders(going_up)` method tells the elevator to stop
(if it's moving), open its doors, pause a second to let riders on and off, and
then close its doors. After all of this is done, the elevator is left in its
IDLE state; it doesn't "remember" what direction it was going before you asked
it to `board_riders`. You'll have to get it moving again with `go_up()` or
`go_down()`. The `going_up` parameter tells the simulation which direction
you're intending to take people who board the elevator on this floor. Think of
it as deciding which indicator light to turn on above the elevator doors so
that "people" waiting on this floor know which direction you're going.

There's also an 'open_doors_to_disembark()' method you can call when you need
to let riders off on a floor, but you don't know of any riders on that floor
that you plan to pick up. Notice that you don't pass it any `going_up`
parameter, because neither the up nor the down arrow lights will light up
when you open your doors on this floor.

Elevator objects also have other methods that aren't intended for controllers
to call. They are features that the simulation uses to manage elevator state.
See "Programming laws," below.

### Things take time

The beating heart of many a simulation is the game loop, which is just a loop
whose iterations represent the passage of time in the game world, and where we
do work on every iteration to update the game world and redraw it.

Time works pretty simplistically in Elevator Yarn. There are no fractional
seconds; everything that happens takes a whole number of seconds to happen.

Here's how long various things take:

```
                                        # seconds
Elevator go up/down one floor           4
Elevator open doors                     1
Elevator close doors                    1
Riders embark/debark after doors open   1 (they're New Yorkers)
```

### Attaching data to elevators

You're likely to want to store some state related to each elevator, and what
better place than on the elevator object itself! You can treat an elevator
object like a `dict`, using key/value access to set and get data:

```python
    an_elevator["my_datum"] = "a datum of mine"
```

### How the game runs and scores

Aside from your controller class and the various classes representing things
in the simulated world (`Elevator`, `Floor`), there are also `Scenario`
objects that drive the actual arrivals and intentions of elevator riders in
the simulated building. They're all implemented in scenarios.py.

For each scenario, Elevator Yarn creates a new building and a new instance of
your controller, and runs the simulation to completion, animating the activity
of elevators and riders with nifty ASCII art. You can use the `--only` flag on
the command line to make Elevator Yarn run a specific subset of scenarios and
then quit.

Scenario objects have an `update()` function enabling them to do as they
please every "second," as do the other objects that represent things in the
simulated world (e.g., Elevator, Floor). While a scenario is running, the game
loop (implemented in the `simulate()` function in run.py) always calls
`update()` functions and event handlers in a particular order. Every "second,"
it first calls the scenario's `update()` function, then your controller's
`update()` functions, and then the other simulation objects' `update()`
function. Then it causes all event handlers to be called for events that
happened during this "second." Then it draws the new state of the building to
your terminal.

For every scenario run, you get some scoring information that includes rides
completed and incomplete (for shame!), the average wait for an elevator and a
"trip efficiency" score that's based on how long completed trips took (only
completed trips are counted) versus an ideal trip duration.

### Programming laws

Attributes and methods of classes whose names start with an underscore are
intended to be private; accessing them in your controller class is essentially
"cheating."

By the same token, you shouldn't attempt to use Elevator and Floor methods
that are public (no underscores in front) but weren't intended for controller
usage, like `riders_boarded()`. Trying to do so will only confuse the
simulation. The same goes for Floor public methods that are intended only for
use by the similator, which is to say _all of them._ Nor should you try to
directly access the Building object.

Not so much a law as a guideline is the use of "_num" to distinguish the names
of Python variables containing floor numbers and those containing Floor
objects. So if you see a function accepting an argument and calling it
"floor," then that should be a Floor object, whereas in all other cases you'd
use a name like "floor_num."

### Messages

A Python programmer usually likes to debug problems by printing to the
terminal, but with the simulator using cursor positioning to animate its ASCII
art building, you can't do this. So Elevator Yarn offers an affordance for
placing messages on the screen as part of the animated display.

Your controller's `update()` function and all of the event handling functions
that you register would normally just return nothing (`None`) implicitly,
because they have no reason for a `return` statement. But you can optionally
return a string from any of these functions, and that string will be decorated
with some information about where and when it's coming from and then added to
a list of messages belonging to the building. Those messages will scroll up on
the right side of the building in the animated display, up to a maximum width
that is conservative by default (40 characters) but which can be expanded with
the `--msgwidth` argument on the command line.

These messages will also be printed out in their entirety after your score
information when a simulated scenario completes. The same will happen if an
exception is raised during the simulation (the exception will be re-raised
afterward, to provide the usual stacktrace).

If the messages are scrolling by too fast, you can slow things down with the
`--speedup` argument on the command line. The default value is 4 (four game
seconds for every real world second), but you can use any factor, including
fractional numbers.
