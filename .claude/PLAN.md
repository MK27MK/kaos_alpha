# algo builder trading game

The game serves as a gentle introduction to systematic trading, allowing
the player to build simple trading systems through a simplified node editor.

## Constraints

- 1 position per time per direction (1 long and 1 short at the same time at max)
- fixed lot size?

### UI

- For each level, the necessary window are pre-disposed and the only thing the user can do is resizing them by the handles.


## Python

- Just simulate daily data. Since we want to get a candlestick representing a fictitious day of price movement, we need to decide if we want to:
  - simulate Brownian motion at a higher frequency (1hr, for example), and then aggregate it to daily.
  - just simulate one path, use it as daily close and calculate high low and open based on some criteria implying randomness.
- I want implement multiple instruments with different properties and create relationships between them as real market instruments have.
  - example: create ficticious currencies with high covariance and a tendency to mean-revert.

## Svelte

- Use svelte xyflow as node builder.

Price is generated in realtime

---

### Levels

In some levels, the type of chart made available is a line, this means a line
chart is enough to solve the puzzle. In others, an OHLC chart is made available.

#### Up and down (line chart tutorial)

use a simple sin function with added noise

#### Timing (line chart)

Price follows an highly volatile brownian motion during some
trading hours, then becomes extremely calm and smooth during a specific part of the day.

#### (Almost) identical twins (line chart)

two gbm with high covariance. Every now and then there is a price discrepancy between the two
and you can trade the spread.

#### Precision (OHLC chart)

Price follows a GBM, but when, by random, closes exactly at a prior williams fractal, then
contrarian returns become more probable for a few iterations. for a few iterations.

---

### Node builder

Limit at 50 nodes or less, if the user tries to place more display the message "Are you trying to decipher Enigma? LIMIT nodes are more than enough for this!"

#### Node types

1. Boolean condition: one input, two outputs (True and False)
2. Entry: long or short
    - if no positions are opened in this direction -> open a new position
3. Exit: long or short (close)
    - if a position is open in this direction -> close it

#### Available variables

Available tools change based on the level in order to make it easily playable.

- hour: int
- price(bars_ago: int = 0) -> float

Indicators:

- sma
- bollinger bands
