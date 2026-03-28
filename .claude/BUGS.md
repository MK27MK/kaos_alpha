## EXISTING

## changing indi parameters inside a condition node cause the chart to flicker

The flicker is caused by a rescaling of price that lasts for a short moment,
while the indicator disappears to be recalculated on the new parameters.

## FIXED

### 1: replay controls stop working after dragging a node

Steps to reproduce:
1. add a node
2. click and drag the node somewhere (not the background), you have to drag, clicking only doesnt trigger the bug
3. try to use replay controls (they won't work)

### adding a bollinger bands node does not plot bollinger bands
steps to reproduce:
1. add a condition node
2. switch left or right value to bb (upper or lower)

BB won't be added to the chart

### changing indicator argument in a condition node cause lwcharts error

steps:
1. add a default condition node
2. change sma period to 10

You'll get this error on every new update until you change len back to its default.
Error: Assertion failed: data must be asc ordered by time, index=12, time=1773857893, prev time=1773857893