import math  # math.sin is faster than numpy sin on scalars
from abc import abstractmethod

import numpy as np

from indicators import Indicator


# NOTE do I need to add memory to them?
class SyntheticInstrument:
    def __init__(self, initial_price: float):
        # TODO cap to 500-1000 values for performance reasons
        # NOTE make it np.array and remove conversion from Indicator.calculate_history?
        self._price_history: list[float] = [initial_price]
        self._initial_price: float = initial_price
        self._current_price: float = initial_price
        self._indicators: dict[str, Indicator] = {}

    @property
    def index(self) -> int:  # where we are in the time/x axis
        return len(self._price_history) - 1

    @abstractmethod
    def _calculate_price(self) -> None:
        pass

    @abstractmethod
    def _calculate_prices(self, n: int) -> np.ndarray:
        """Generate an array of n prices (vectorized, for backtesting)."""
        pass

    def get_params(self) -> dict:
        """Return constructor params so a fresh copy can be spawned for backtesting."""
        return {"initial_price": self._initial_price}

    def add_indicator(self, indicator: Indicator) -> None:
        # Deduplication is handled by the frontend — if we get here, it's a new indicator
        indicator.calculate_history(self._price_history)
        self._indicators[indicator.key] = indicator

    def remove_indicator(self, key: str) -> None:
        self._indicators.pop(key, None)

    def get_indicator(self, key: str) -> Indicator | None:
        return self._indicators.get(key)

    @property
    def indicators(self):
        return self._indicators

    def get_new_price(self) -> float:
        self._calculate_price()
        self._update_history()

        # Update all indicators with the new price
        for indicator in self._indicators.values():
            indicator.update(self._current_price)

        return self._current_price

    def reset_history(self):
        self._price_history: list[float] = [self._initial_price]
        self._current_price = self._initial_price
        self._indicators.clear()

    def _update_history(self) -> None:
        self._price_history.append(self._current_price)


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

    def get_params(self) -> dict:
        return {
            **super().get_params(),
            "amplitude": self._amplitude,
            "period": self._period,
            "noise_std": self._noise_std,
        }

    def _calculate_price(self) -> None:
        sin_component = self._amplitude * math.sin(
            2 * math.pi * self.index / self._period
        )
        noise = np.random.normal(0, self._noise_std)
        self._current_price = self._initial_price + sin_component + noise

    def _calculate_prices(self, n: int) -> np.ndarray:
        indices = np.arange(n)
        sin_component = self._amplitude * np.sin(2 * np.pi * indices / self._period)
        noise = np.random.normal(0, self._noise_std, size=n)
        return self._initial_price + sin_component + noise


# NOTE difference between arithmetic and geom. GBM?
class GeometricBrownianMotion(SyntheticInstrument):
    pass


# ...
# ...
# ...
