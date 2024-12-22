# weather-factory

Weather Factory is a WIP SPSA tuner for UCI compliant chess engines.

Usage instructions:

make a folder "tuner"
Put the opening book and the engine binary in the folder.
If the cutechess-cli or fastchess binary are not in the PATH environment variable you have to put one of them into the "tuner" folder as well.
It is suggested to use fastchess, since it has less overhead.

Change the .json config files following the format presented.

Each parameter in config.json should correspond to one UCI parameter:

```
option name TEST type spin default 100 min 50 max 150
```
```json
"TEST": {
    "value": 100,
    "min_value": 50,
    "max_value": 150,
    "step": 10
}
```
the step parameter should be large enough to create a 2-3 elo difference.

For the SPSA config file, none of the values used in spsa.json except "A" require changing. Ideally `A = max iterations / 10`.

cutechess.json:
```
engine: name of the engine inside the `tuner` folder

book: name of the book inside the `tuner` folder

games: number of games played per SPSA iteration, make sure this is a multiple of two and ideally a multiple of threads.

tc: The time control the matches are going to be played at. Increment is automatically `tc / 100`.

threads: This corresponds to concurrency it cutechess, not the threads of the engine.

pgnout: The filepath to the PGN all the games played should be saved to.

save_rate: The number of games between times saving the state to a file

use_fastchess: Set to true of you want to use fastchess and set to false if you want to use cutechess
```

