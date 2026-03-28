import asyncio
import time

import numpy as np
from backtest import Backtester
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from indicators import Indicator
from processes import NoisySin

from app.model import AddIndicatorResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level globals so REST endpoints can access the instrument state
instrument = NoisySin()
sim_time_start: int = 0


@app.get("/health")
def health():
    return {"status": "ok"}


# REST endpoints for indicator management ==============================


@app.post("/api/indicators", response_model=AddIndicatorResponse)
def add_indicator(indicator: Indicator):
    instrument.add_indicator(indicator)
    return AddIndicatorResponse(indicator_key=indicator.key)


@app.get(
    "/api/indicators/{indicator_key}/history",
    response_model=dict[str, list[float | None]],
)
def get_indicator_history(indicator_key: str):
    if indicator_key is None:
        return JSONResponse({"error": "Indicator not found"}, status_code=404)

    history = instrument.get_indicator(indicator_key).history

    # Replace NaN with None so it serializes to JSON null
    return history.replace({np.nan: None}).to_dict(orient="list")


@app.delete("/api/indicators/{indicator_key}")
def delete_indicator(indicator_key: str):
    instrument.remove_indicator(indicator_key)
    return {"status": "ok"}


@app.post("/api/backtest")
def run_backtest(strategy: dict):
    """Run vectorized backtest on freshly generated data (independent of the live stream)."""

    backtester = Backtester(
        instrument_class=instrument.__class__,
        instrument_params=instrument.get_params(),
    )
    return backtester.run(strategy)


# WebSocket price stream ===============================================


@app.websocket("/ws/price-stream")
async def price_stream(ws: WebSocket):
    global instrument, sim_time_start
    await ws.accept()

    instrument = NoisySin()
    base_interval = 0.5
    speed = 1.0
    paused = False
    sim_time = int(time.time())
    sim_time_start = sim_time

    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_json(), timeout=0.01)
                if msg.get("type") == "control":
                    action = msg.get("action")
                    if action == "pause":
                        paused = True
                    elif action == "resume":
                        paused = False
                    elif action == "reset":
                        instrument = NoisySin()
                        sim_time = int(time.time())
                        sim_time_start = sim_time
                        paused = False
                    elif action == "speed":
                        speed = max(0.1, min(10.0, float(msg.get("value", 1.0))))
            except asyncio.TimeoutError:
                pass

            if paused:
                await asyncio.sleep(0.05)
                continue

            price = instrument.get_new_price()
            await ws.send_json(
                {
                    "type": "price",
                    "time": sim_time,
                    "value": round(price, 2),
                }
            )

            # Send indicator tick values
            for indicator in instrument.indicators.values():
                val = indicator.current_value
                if val is None:
                    continue

                if isinstance(val, dict):
                    # Multi-band indicator (BB): send ONE message with all band values
                    await ws.send_json(
                        {
                            "type": "indicator",
                            "key": indicator.key,
                            "time": sim_time,
                            "value": {k: round(v, 4) for k, v in val.items()},
                        }
                    )
                else:
                    await ws.send_json(
                        {
                            "type": "indicator",
                            "key": indicator.key,
                            "time": sim_time,
                            "value": round(float(val), 4),
                        }
                    )

            sim_time += 60
            await asyncio.sleep(base_interval / speed)
    except WebSocketDisconnect:
        pass
