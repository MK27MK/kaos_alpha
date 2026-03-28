"""Vectorized backtest engine.

Receives a strategy DAG from the frontend, generates fresh price data,
evaluates conditions and propagates signals through the graph, then
simulates positions bar-by-bar.
"""

import time
from collections import deque

import numpy as np
from indicators import BollingerBands

# ── Feature computation ──────────────────────────────────────────────


def _feature_key(market_feature: dict) -> str:
    """Deterministic cache key for a serialized feature."""
    feat_type = market_feature["type"]
    feature_data = market_feature.get("parameters", {})
    match feat_type:
        case "price":
            return f"price:{feature_data.get('barsAgo', 0)}"
        case "sma":
            return f"sma:{feature_data['length']}"
        case "bollinger_bands":
            return f"bollinger_bands:{feature_data.get('band', 'upper')}:{feature_data['length']}:{feature_data.get('stDev', 2)}"

    return feat_type  # "hour"


def _compute_feature(
    feature: dict, prices: np.ndarray, times: np.ndarray
) -> np.ndarray:
    """Return a float64 array of length N for the given feature."""
    feature_type = feature["type"]
    parameters = feature.get("parameters", {})
    n_bars = len(prices)

    if feature_type == "price":
        bars_ago = parameters.get("barsAgo", 0)
        if bars_ago == 0:
            return prices.copy()
        result = np.full(n_bars, np.nan)
        if bars_ago < n_bars:
            result[bars_ago:] = prices[: n_bars - bars_ago]
        return result

    if feature_type == "sma":
        length = parameters["length"]
        if n_bars < length:
            return np.full(n_bars, np.nan)
        kernel = np.ones(length) / length
        sma = np.convolve(prices, kernel, mode="valid")
        result = np.full(n_bars, np.nan)
        result[length - 1 :] = sma
        return result

    if feature_type == "bollinger_bands":
        length = parameters["length"]
        std_dev = parameters.get("stDev", 2)
        band = parameters.get("band", "upper")
        if n_bars < length:
            return np.full(n_bars, np.nan)
        upper, middle, lower = BollingerBands.compute_bands(prices, length, std_dev)
        result = np.full(n_bars, np.nan)
        result[length - 1 :] = upper if band == "upper" else lower
        return result

    if feature_type == "hour":
        return ((times % 86400) // 3600).astype(np.float64)

    raise ValueError(f"Unknown feature type: {feature_type}")


# ── Condition evaluation ─────────────────────────────────────────────


_OPERATORS = {
    "<": np.less,
    ">": np.greater,
    "<=": np.less_equal,
    ">=": np.greater_equal,
    "!=": lambda a, b: ~np.isclose(a, b, atol=1e-9),
    "=": lambda a, b: np.isclose(a, b, atol=1e-9),
}


def _evaluate_condition(cond: dict, feature_cache: dict[str, np.ndarray]) -> np.ndarray:
    left = feature_cache[_feature_key(cond["left"])]
    right = feature_cache[_feature_key(cond["right"])]
    op_fn = _OPERATORS[cond["operator"]]
    # NaN comparisons naturally yield False — warmup bars won't fire
    result = op_fn(left, right)
    # Force any NaN-originating values to False
    result[np.isnan(left) | np.isnan(right)] = False
    return result


# ── DAG signal propagation ───────────────────────────────────────────


def _topological_sort(roots: list[str], edges: dict, actions: dict) -> list[str]:
    """BFS-based topological ordering of the strategy DAG."""
    order = []
    visited = set()
    queue = deque(roots)

    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        order.append(node_id)

        if node_id in edges:
            for branch in ("true", "false"):
                for child_id in edges[node_id].get(branch, []):
                    if child_id not in visited:
                        queue.append(child_id)

    return order


def _compute_signals(
    strategy: dict, condition_results: dict[str, np.ndarray], n_bars: int
) -> dict[str, np.ndarray]:
    """Propagate reachability masks through the DAG. Returns bool arrays per action node."""
    topo = _topological_sort(strategy["roots"], strategy["edges"], strategy["actions"])

    reachable: dict[str, np.ndarray] = {}

    for node_id in topo:
        # Root conditions are always reachable
        if node_id in strategy["roots"] and node_id not in reachable:
            reachable[node_id] = np.ones(n_bars, dtype=bool)

        if node_id not in reachable:
            continue

        if node_id in strategy["conditions"]:
            cond_result = condition_results[node_id]
            parent_mask = reachable[node_id]

            true_mask = parent_mask & cond_result
            false_mask = parent_mask & ~cond_result

            for child_id in strategy["edges"].get(node_id, {}).get("true", []):
                if child_id in reachable:
                    reachable[child_id] = reachable[child_id] | true_mask
                else:
                    reachable[child_id] = true_mask.copy()

            for child_id in strategy["edges"].get(node_id, {}).get("false", []):
                if child_id in reachable:
                    reachable[child_id] = reachable[child_id] | false_mask
                else:
                    reachable[child_id] = false_mask.copy()

    signals = {}
    for action_id in strategy["actions"]:
        signals[action_id] = reachable.get(action_id, np.zeros(n_bars, dtype=bool))

    return signals


# ── Position simulation ──────────────────────────────────────────────


def _simulate_positions(
    signals: dict[str, np.ndarray],
    actions: dict[str, dict],
    prices: np.ndarray,
    n_bars: int,
) -> tuple[list[dict], list[float]]:
    """Sequential bar-by-bar position tracking. Exits process before entries."""
    long_open = False
    short_open = False
    long_entry_price = 0.0
    short_entry_price = 0.0
    long_entry_bar = -1
    short_entry_bar = -1

    trades: list[dict] = []
    equity = np.zeros(n_bars)
    cumulative_pnl = 0.0

    for i in range(n_bars):
        # Collect firing actions for this bar
        firing_exits = []
        firing_entries = []
        for action_id, signal in signals.items():
            if signal[i]:
                action = actions[action_id]
                if action["type"] == "exit":
                    firing_exits.append(action)
                else:
                    firing_entries.append(action)

        # Process exits first — frees slots for entries on the same bar
        for action in firing_exits:
            if action["direction"] == "buy" and long_open:
                pnl = prices[i] - long_entry_price
                trades.append(
                    {
                        "entry_bar": long_entry_bar,
                        "exit_bar": i,
                        "direction": "long",
                        "entry_price": round(float(long_entry_price), 4),
                        "exit_price": round(float(prices[i]), 4),
                        "pnl": round(float(pnl), 4),
                    }
                )
                cumulative_pnl += pnl
                long_open = False
            elif action["direction"] == "sell" and short_open:
                pnl = short_entry_price - prices[i]
                trades.append(
                    {
                        "entry_bar": short_entry_bar,
                        "exit_bar": i,
                        "direction": "short",
                        "entry_price": round(float(short_entry_price), 4),
                        "exit_price": round(float(prices[i]), 4),
                        "pnl": round(float(pnl), 4),
                    }
                )
                cumulative_pnl += pnl
                short_open = False

        # Process entries
        for action in firing_entries:
            if action["direction"] == "buy" and not long_open:
                long_open = True
                long_entry_price = prices[i]
                long_entry_bar = i
            elif action["direction"] == "sell" and not short_open:
                short_open = True
                short_entry_price = prices[i]
                short_entry_bar = i

        # Equity = realized + unrealized PnL
        unrealized = 0.0
        if long_open:
            unrealized += prices[i] - long_entry_price
        if short_open:
            unrealized += short_entry_price - prices[i]
        equity[i] = cumulative_pnl + unrealized

    return trades, equity.tolist()


# ── Public API ───────────────────────────────────────────────────────


class Backtester:
    def __init__(self, instrument_class, instrument_params: dict, n_bars: int = 10_000):
        self._instrument_class = instrument_class
        self._instrument_params = instrument_params
        self._n_bars = n_bars

    def run(self, strategy: dict) -> dict:
        # Phase 0: generate fresh price data
        instrument = self._instrument_class(**self._instrument_params)
        prices = instrument._calculate_prices(self._n_bars)
        base_time = int(time.time())
        times = np.arange(self._n_bars) * 60 + base_time

        n_bars = self._n_bars

        # Phase 1: compute feature arrays (deduplicated)
        feature_cache: dict[str, np.ndarray] = {}
        for cond in strategy["conditions"].values():
            for side in ("left", "right"):
                key = _feature_key(cond[side])
                if key not in feature_cache:
                    feature_cache[key] = _compute_feature(cond[side], prices, times)

        # Phase 2: evaluate each condition to a bool array
        condition_results: dict[str, np.ndarray] = {}
        for node_id, cond in strategy["conditions"].items():
            condition_results[node_id] = _evaluate_condition(cond, feature_cache)

        # Phase 3: propagate signals through the DAG
        signals = _compute_signals(strategy, condition_results, n_bars)

        # Phase 4: simulate positions
        trades, equity = _simulate_positions(
            signals, strategy["actions"], prices, n_bars
        )

        # Build response
        entry_markers = []
        exit_markers = []
        for trade in trades:
            entry_markers.append(
                {
                    "time": int(times[trade["entry_bar"]]),
                    "direction": trade["direction"],
                }
            )
            if trade["exit_bar"] >= 0:
                exit_markers.append(
                    {
                        "time": int(times[trade["exit_bar"]]),
                        "direction": trade["direction"],
                    }
                )

        equity_curve = [
            {"time": int(times[i]), "value": round(equity[i], 4)} for i in range(n_bars)
        ]

        # Summary stats
        total_trades = len(trades)
        winning = [t for t in trades if t["pnl"] > 0]
        losing = [t for t in trades if t["pnl"] <= 0]
        total_pnl = sum(t["pnl"] for t in trades)

        # Max drawdown from equity curve
        peak = -np.inf
        max_dd = 0.0
        for val in equity:
            if val > peak:
                peak = val
            dd = val - peak
            if dd < max_dd:
                max_dd = dd

        summary = {
            "total_trades": total_trades,
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "total_pnl": round(total_pnl, 4),
            "max_drawdown": round(max_dd, 4),
            "win_rate": (
                round(len(winning) / total_trades, 4) if total_trades > 0 else 0
            ),
        }

        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "entry_markers": entry_markers,
            "exit_markers": exit_markers,
            "summary": summary,
        }
