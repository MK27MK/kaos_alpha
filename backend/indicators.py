from abc import ABC, abstractmethod
from collections import deque

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

# TODO do camelcase model


class Indicator(BaseModel, ABC):
    # Allow pd.DataFrame as a field type — Pydantic doesn't know
    # how to build a JSON schema for it, so we need this escape hatch.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    parameters: dict[str, int | float]
    history: pd.DataFrame = Field(default_factory=pd.DataFrame)
    _buffer: deque = PrivateAttr(default_factory=deque)

    @property
    def key(self) -> str:
        parameters_values = ":".join(str(v) for v in self.parameters.values())
        return f"{self.name}:{parameters_values}"

    @abstractmethod
    def calculate_history(self, prices: list[float]) -> None:
        """Vectorized bulk computation using numpy. Populates history and fills _buffer."""

    @abstractmethod
    def update(self, price: float):
        """Incremental computation for a single new price. Appends to history. Returns new value."""

    @property
    @abstractmethod
    def current_value(self):
        """Return the most recent indicator value, or None if not enough data yet."""


class SMA(Indicator):
    def __init__(self, arguments: dict[str, int]):
        super().__init__(name="sma", parameters=arguments)
        self._buffer = deque(maxlen=arguments["length"])

    def calculate_history(self, prices: list[float]) -> None:
        length = int(self.parameters["length"])
        prices_array = np.array(prices, dtype=np.float64)

        # there isnt enough data to calculate the indicator yet
        if len(prices_array) < length:
            self.history = pd.DataFrame({"value": [np.nan] * len(prices_array)})
            self._buffer = deque(prices, maxlen=length)
            return

        # Vectorized SMA via convolution
        kernel = np.ones(length) / length
        sma_values = np.convolve(prices_array, kernel, mode="valid")

        values = [np.nan] * (length - 1) + sma_values.tolist()
        self.history = pd.DataFrame({"value": values})

        # Fill buffer with the last `length` prices for incremental updates
        self._buffer = deque(prices[-length:], maxlen=length)

    def update(self, price: float):
        self._buffer.append(price)
        length = int(self.parameters["length"])

        if len(self._buffer) < length:
            value = np.nan
        else:
            value = sum(self._buffer) / length

        new_row = pd.DataFrame({"value": [value]})
        self.history = pd.concat([self.history, new_row], ignore_index=True)
        return None if np.isnan(value) else value

    @property
    def current_value(self):
        if self.history.empty:
            return None
        last_value = self.history["value"].iloc[-1]
        return None if np.isnan(last_value) else float(last_value)


class BollingerBands(Indicator):
    def __init__(self, arguments: dict[str, int]):
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
            self.history = pd.DataFrame(
                {
                    "upper": [np.nan] * nan_count,
                    "middle": [np.nan] * nan_count,
                    "lower": [np.nan] * nan_count,
                }
            )
            self._buffer = deque(prices, maxlen=length)
            return

        upper_band, middle_band, lower_band = self.compute_bands(
            prices_array, length, std_dev
        )

        nan_prefix = [np.nan] * (length - 1)
        self.history = pd.DataFrame(
            {
                "upper": nan_prefix + upper_band.tolist(),
                "middle": nan_prefix + middle_band.tolist(),
                "lower": nan_prefix + lower_band.tolist(),
            }
        )

        self._buffer = deque(prices[-length:], maxlen=length)

    def update(self, price: float):
        self._buffer.append(price)
        length = int(self.parameters["length"])
        std_dev = self.parameters["std_dev"]

        if len(self._buffer) < length:
            new_row = pd.DataFrame(
                {
                    "upper": [np.nan],
                    "middle": [np.nan],
                    "lower": [np.nan],
                }
            )
        else:
            window = list(self._buffer)
            middle = sum(window) / length
            variance = sum((p - middle) ** 2 for p in window) / length
            std = variance**0.5
            new_row = pd.DataFrame(
                {
                    "upper": [middle + std_dev * std],
                    "middle": [middle],
                    "lower": [middle - std_dev * std],
                }
            )

        self.history = pd.concat([self.history, new_row], ignore_index=True)

        last = self.history.iloc[-1]
        if np.isnan(last["upper"]):
            return None
        return {
            "upper": float(last["upper"]),
            "middle": float(last["middle"]),
            "lower": float(last["lower"]),
        }

    @property
    def current_value(self):
        if self.history.empty:
            return None
        last = self.history.iloc[-1]
        if np.isnan(last["upper"]):
            return None
        return {
            "upper": float(last["upper"]),
            "middle": float(last["middle"]),
            "lower": float(last["lower"]),
        }
