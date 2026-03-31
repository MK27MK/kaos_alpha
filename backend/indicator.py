from abc import ABC, abstractmethod
from collections import deque

import numpy as np
from app.data_model.indicator_schema import IndicatorParameters, make_indicator_key
from pydantic import BaseModel, PrivateAttr

# TODO do camelcase model


class Indicator(BaseModel, ABC):
    name: str
    parameters: IndicatorParameters
    history: dict[str, list[float | None]] = {}
    _buffer: deque = PrivateAttr(default_factory=deque)

    @property
    def key(self) -> str:
        return make_indicator_key(self.name, self.parameters)

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
    def __init__(self, arguments: IndicatorParameters):
        super().__init__(name="sma", parameters=arguments)
        self._buffer = deque(maxlen=arguments["length"])

    def calculate_history(self, prices: list[float]) -> None:
        length = int(self.parameters["length"])
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
        length = int(self.parameters["length"])

        # NA if buffer is too short yet, the avg of the buffer otherwise
        new_value = None if len(self._buffer) < length else sum(self._buffer) / length

        self._append_new_value({"value": new_value})


class BollingerBands(Indicator):
    def __init__(self, arguments: IndicatorParameters):
        super().__init__(name="bollinger_bands", parameters=arguments)
        self._buffer = deque(maxlen=arguments["length"])

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
        length = int(self.parameters["length"])
        std_dev = self.parameters["std_dev"]
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
            prices_array, length, std_dev
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
        length = int(self.parameters["length"])
        std_dev = self.parameters["std_dev"]

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


class Price(Indicator):
    def __init__(self, arguments: dict[str, int | float] = {}):
        super().__init__(name="price", parameters=arguments)

    def calculate_history(self, prices: list[float]) -> None:
        self.history = {"value": list(prices)}

    def update(self, price: float):
        self._append_new_value({"value": price})


class Hour(Indicator):
    _start_time: int = PrivateAttr(default=0)
    _tick_count: int = PrivateAttr(default=0)

    def __init__(self, arguments: dict[str, int | float] = {}):
        import time

        super().__init__(name="hour", parameters=arguments)
        self._start_time = int(time.time())
        self._tick_count = 0

    def calculate_history(self, prices: list[float]) -> None:
        n = len(prices)
        # Reconstruct hours for historical bars (each bar = 60 sim-seconds)
        base = self._start_time - n * 60
        self.history = {
            "value": [float(((base + i * 60) % 86400) // 3600) for i in range(n)]
        }
        self._tick_count = n

    def update(self, price: float):
        current_time = self._start_time + self._tick_count * 60
        hour = float((current_time % 86400) // 3600)
        self._append_new_value({"value": hour})
        self._tick_count += 1
