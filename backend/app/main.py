import asyncio
import time

from backtest import Backtester
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from indicator import SMA, BollingerBands, Hour, Price
from instrument import NoisySin

from app.data_model.indicator_schema import INDICATOR_SCHEMAS, IndicatorSchema
from app.data_model.model import AddIndicatorRequest, AddIndicatorResponse

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


# REST endpoints for indicator schemas ==================================


@app.get("/api/indicator-schemas", response_model=list[IndicatorSchema])
def get_indicator_schemas():
    return list(INDICATOR_SCHEMAS.values())


# REST endpoints for indicator management ==============================


@app.post("/api/indicators", response_model=AddIndicatorResponse)
def add_indicator(request: AddIndicatorRequest):
    indicator_class_map = {
        "bollinger_bands": BollingerBands,
        "sma": SMA,
        "price": Price,
        "hour": Hour,
    }
    child_class = indicator_class_map[request.name]
    indicator_instance = child_class(arguments=request.parameters)
    instrument.add_indicator(indicator_instance)
    return AddIndicatorResponse(indicator_key=indicator_instance.key)


@app.get(
    "/api/indicators/{indicator_key}/history",
    response_model=dict[str, list[float | None]],
)
def get_indicator_history(indicator_key: str):
    indicator = instrument.get_indicator(indicator_key)
    if indicator is None:
        return JSONResponse({"error": "Indicator not found"}, status_code=404)

    return indicator.history


@app.delete("/api/indicators/{indicator_key}")
def delete_indicator(indicator_key: str):
    instrument.remove_indicator(indicator_key)
    return {"status": "ok"}


@app.post("/api/backtest")
def run_backtest(strategy: dict):
    """Run vectorized backtest on freshly generated data (independent of the live stream)."""

    backtester = Backtester(
        instrument_class=instrument.__class__,
        instrument_params=instrument.to_dict(),
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

            new_point = instrument.get_new_point()
            await ws.send_json(
                {
                    "type": "price",
                    "value": new_point,
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
                            "time": new_point.time,
                            "value": val,
                        }
                    )
                else:
                    await ws.send_json(
                        {
                            "type": "indicator",
                            "key": indicator.key,
                            "time": new_point.time,
                            "value": round(float(val), 4),
                        }
                    )

            await asyncio.sleep(base_interval / speed)
    except WebSocketDisconnect:
        pass
