from abc import ABC, abstractmethod
from collections import deque

import numpy as np
from pydantic import BaseModel, PrivateAttr

# TODO do camelcase model


class Indicator(BaseModel, ABC):
    name: str
    history: dict[str, list[float | None]] = {}
    _buffer: deque = PrivateAttr(default_factory=deque)

    @property
    @abstractmethod
    def key(self) -> str:
        pass

    @abstractmethod
    def calculate_history(self, prices: list[float]) -> None:
        """Vectorized bulk computation using numpy. Populates history and fills _buffer."""

    @abstractmethod
    def update(self, price: float):
        """Incremental computation for a single new price. Appends to history. Returns new value."""

    @property
    def current_value(self):
        """Return the most recent indicator value, or None if not enough data yet."""
        if not self.history:
            return None
        return {k: v[-1] for k, v in self.history.items()}

    def _append_new_value(self, new_value: dict[str, float | None]):
        for key in new_value:
            self.history[key].append(new_value[key])


class SMA(Indicator):
    name: str = "sma"
    length: int

    @property
    def key(self) -> str:
        return f"sma:{self.length}"

    def calculate_history(self, prices: list[float]) -> None:
        length = int(self.length)
        prices_array = np.array(prices, dtype=np.float64)

        # there isnt enough data to calculate the indicator yet
        if len(prices_array) < length:
            self.history = {"value": [None] * len(prices_array)}
            self._buffer = deque(prices, maxlen=length)
            return

        # Vectorized SMA via convolution
        kernel = np.ones(length) / length
        sma_values = np.convolve(prices_array, kernel, mode="valid")

        values = [None] * (length - 1) + sma_values.tolist()
        self.history = {"value": values}

        # Fill buffer with the last `length` prices for incremental updates
        self._buffer = deque(prices[-length:], maxlen=length)

    def update(self, price: float):
        self._buffer.append(price)
        length = int(self.length)

        # NA if buffer is too short yet, the avg of the buffer otherwise
        new_value = None if len(self._buffer) < length else sum(self._buffer) / length

        self._append_new_value({"value": new_value})


class BollingerBands(Indicator):
    name: str = "bollinger_bands"
    length: int
    std_dev: float

    @property
    def key(self) -> str:
        # :g strips trailing ".0" so key matches make_indicator_key(raw_params)
        # e.g. std_dev=2.0 → "2" instead of "2.0"
        return f"bollinger_bands:{self.length}:{self.std_dev:g}"

    @staticmethod
    def compute_bands(
        prices_array: np.ndarray, length: int, std_dev: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Vectorized rolling mean/std → (upper, middle, lower) arrays of len(prices) - length + 1."""
        # Rolling mean via sliding window cumsum trick
        # NOTE approfondisci
        cumsum = np.concatenate([[0], np.cumsum(prices_array)])
        rolling_mean = (cumsum[length:] - cumsum[:-length]) / length

        # Rolling std (population std)
        sq_cumsum = np.concatenate([[0], np.cumsum(prices_array**2)])
        mean_sq = (sq_cumsum[length:] - sq_cumsum[:-length]) / length
        rolling_std = np.sqrt(np.maximum(mean_sq - rolling_mean**2, 0))

        upper = rolling_mean + std_dev * rolling_std
        lower = rolling_mean - std_dev * rolling_std
        return upper, rolling_mean, lower

    def calculate_history(self, prices: list[float]) -> None:
        length = int(self.length)
        prices_array = np.array(prices, dtype=np.float64)

        # There isn't enough data to calculate any indicator values,
        # So let's fill with NaN all the price points for which we
        # do not have a corresponding indicator value
        if len(prices_array) < length:
            nan_count = len(prices_array)
            self.history = {
                "upper": [None] * nan_count,
                "middle": [None] * nan_count,
                "lower": [None] * nan_count,
            }

            self._buffer = deque(prices, maxlen=length)
            return

        upper_band, middle_band, lower_band = self.compute_bands(
            prices_array, length, self.std_dev
        )

        nan_prefix = [None] * (length - 1)
        self.history = {
            "upper": nan_prefix + upper_band.tolist(),
            "middle": nan_prefix + middle_band.tolist(),
            "lower": nan_prefix + lower_band.tolist(),
        }

        self._buffer = deque(prices[-length:], maxlen=length)

    def update(self, price: float):
        self._buffer.append(price)
        length = int(self.length)
        std_dev = self.std_dev

        if len(self._buffer) < length:
            new_value: dict[str, float | None] = {
                "upper": None,
                "middle": None,
                "lower": None,
            }

        else:
            window = list(self._buffer)
            middle = sum(window) / length
            variance = sum((p - middle) ** 2 for p in window) / length
            std = variance**0.5
            new_value = {
                "upper": float(middle + std_dev * std),
                "middle": float(middle),
                "lower": float(middle - std_dev * std),
            }

        self._append_new_value(new_value)
