# MonopolySim

**MonopolySim** is a command-line Monopoly simulator, written in Python.

## Requirements

* A terminal window.
* Python 2.7+

## Usage

Execute the `./run_game.py` script. The `sim.log` logfile will output the results of the game.

## Configuration

Change the number of players (default: `2`):

```
./run_game.py --players 5
```

Change the locale (default: `en-gb`):

Note: currently only `en-gb` is setup, but more locales will follow.

```
./run_game.py --locale fr-fr
```

Run the game in 'fast mode' (i.e. with no artificial delay of 0.25s between turns):

```
./run_game.py --fast
```



