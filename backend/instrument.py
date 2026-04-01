import math  # math.sin is faster than numpy sin on scalars
import time as _time
from abc import ABC, abstractmethod
from collections import deque
from typing import NamedTuple

import numpy as np
from indicator import Indicator


class PricePoint(NamedTuple):
    price: float
    time: int  # Unix timestamp in seconds


class SyntheticInstrument(ABC):
    def __init__(self, initial_price: float, max_len: int = 1000):
        self._max_len = max_len
        self._initial_point = PricePoint(initial_price, int(_time.time()))
        self._current_point = self._initial_point

        self._price_points = deque([self._initial_point], max_len)
        self._indicators: dict[str, Indicator] = {}

    @property
    def index(self) -> int:  # where we are in the time/x axis
        return len(self._price_points) - 1

    @property
    def indicators(self):
        return self._indicators

    def get_new_point(self) -> PricePoint:
        self._make_new_point()
        self._update_price_points()
        self._update_indicators()

        return self._current_point

    def get_new_points(self, n_of_points: int) -> list[PricePoint]:
        return [self.get_new_point() for _ in range(n_of_points)]

    def get_historical_point(self, bars_ago: int = 0) -> PricePoint:
        # -1 -> last bar (0 bars_ago), -2 -> 1 bar ago ...
        return self._price_points[-(1 + bars_ago)]

    def to_dict(self) -> dict:
        """Return constructor params so a fresh copy can be spawned for backtesting."""
        return {"initial_price": self._initial_point.price}

    # indicator methods ------------------------------------------------

    def add_indicator(self, indicator: Indicator) -> None:
        # Deduplication is handled by the frontend — if we get here, it's a new indicator
        indicator.calculate_history([p.price for p in self._price_points])
        self._indicators[indicator.key] = indicator

    def remove_indicator(self, key: str) -> None:
        self._indicators.pop(key, None)

    def get_indicator(self, key: str) -> Indicator | None:
        return self._indicators.get(key)

    def reset_price_points(self) -> None:
        self._initial_point = PricePoint(self._initial_point.price, int(_time.time()))
        self._price_points = deque([self._initial_point], 1000)
        self._current_point = self._initial_point
        self._indicators.clear()

    # helpers ----------------------------------------------------------

    def _update_price_points(self) -> None:
        self._price_points.append(self._current_point)

    def _update_indicators(self) -> None:
        # Update all indicators with the new price
        for indicator in self._indicators.values():
            indicator.update(self._current_point.price)

    def _get_new_time(self) -> int:
        # Each tick advances by 1 minute - lightweight-charts expects Unix timestamps
        return self._current_point.time + 60

    def _make_new_point(self) -> None:
        self._current_point = PricePoint(self._get_new_price(), self._get_new_time())

    @abstractmethod
    def _get_new_price(self) -> float:
        """Contains the logic which generates a new price.

        Returns
        -------
        float
            Price generated.
        """
        pass

    @abstractmethod
    def _get_new_prices(self, n: int) -> np.ndarray:
        """Generate an array of n prices (vectorized, for backtesting)."""
        pass


class NoisySin(SyntheticInstrument):
    def __init__(
        self,
        initial_price: float = 100.0,
        amplitude: float = 10.0,
        period: int = 50,
        noise_std: float = 1.0,
    ):
        super().__init__(initial_price)
        self._amplitude = amplitude
        self._period = period
        self._noise_std = noise_std

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "amplitude": self._amplitude,
            "period": self._period,
            "noise_std": self._noise_std,
        }

    def _get_new_price(self) -> float:
        sin_component = self._amplitude * math.sin(
            2 * math.pi * self.index / self._period
        )
        noise = np.random.normal(0, self._noise_std)
        return self._initial_point.price + sin_component + noise

    def _get_new_prices(self, n: int) -> np.ndarray:
        indices = np.arange(n)
        sin_component = self._amplitude * np.sin(2 * np.pi * indices / self._period)
        noise = np.random.normal(0, self._noise_std, size=n)
        return self._initial_point.price + sin_component + noise


# NOTE difference between arithmetic and geom. GBM?
class GeometricBrownianMotion(SyntheticInstrument):
    pass


# ...
# ...
# ...
