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

## How to Play

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

There's a DumbController class, in dumb_controller.py, to serve as an example.

### Things Take Time

The beating heart of many a simulation is the game loop, which is just a loop
whose iterations represent the passage of time in the game world, and where we
do work on every iteration to update the game world and redraw it.

Time works pretty simplistically in Elevator Yarn. There are no fractional
seconds; everything that happens takes a whole number of seconds to happen.

Here's how long various things take:

```
                                           # seconds
Elevator go up/down one floor              4
Elevator open doors                        1
Elevator close doors                       1
Riders embark/debark while doors are open  1 (they're New Yorkers)
```

### Physical Laws

If an elevator is moving in a direction, you can't just tell it to move
instantaneously in the opposite direction. You have to stop it first.
Otherwise, you'll blow the elevator's transmission.

### Scoring

Your final score is based on how well you served your riders.
