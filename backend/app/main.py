import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from indicator import SMA, BollingerBands
from instrument import NoisySin

from app.data_model.model import (
    AddIndicatorRequest,
    AddIndicatorResponse,
    ControlMessage,
    IndicatorMessage,
    PriceMessage,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level global so REST endpoints can access the instrument state
instrument = NoisySin()


@app.get("/health")
def health():
    return {"status": "ok"}


# REST endpoints for indicator management ==============================


@app.post("/api/indicators", response_model=AddIndicatorResponse)
def add_indicator(request: AddIndicatorRequest):
    indicator_class_map = {
        "bollinger_bands": BollingerBands,
        "sma": SMA,
        # "price": Price,
        # "hour": Hour,
    }
    child_class = indicator_class_map[request.name]
    indicator_instance = child_class(parameters=request.parameters)
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


# @app.post("/api/backtest")
# def run_backtest(strategy: dict):
#     """Run vectorized backtest on freshly generated data (independent of the live stream)."""

#     backtester = Backtester(
#         instrument_class=instrument.__class__,
#         instrument_params=instrument.to_dict(),
#     )
#     return backtester.run(strategy)


# WebSocket price stream ===============================================


@app.websocket("/ws/price-stream")
async def price_stream(ws: WebSocket):
    global instrument
    await ws.accept()

    instrument = NoisySin()
    base_interval = 0.5
    speed = 1.0
    paused = False

    try:
        while True:
            try:
                raw_msg = await asyncio.wait_for(ws.receive_json(), timeout=0.01)
                control = ControlMessage.model_validate(raw_msg)
                match control.action:
                    case "pause":
                        paused = True
                    case "resume":
                        paused = False
                    case "reset":
                        instrument = NoisySin()
                        paused = False
                    case "speed":
                        speed = max(0.1, min(10.0, control.value or 1.0))
            except asyncio.TimeoutError:
                pass

            if paused:
                await asyncio.sleep(0.05)
                continue

            new_point = instrument.get_new_point()
            price_msg = PriceMessage(time=new_point.time, value=new_point.price)
            await ws.send_json(price_msg.model_dump())

            # Send indicator tick values
            for indicator in instrument.indicators.values():
                val = indicator.current_value
                if val is None:
                    continue

                indicator_msg = IndicatorMessage(
                    key=indicator.key,
                    time=new_point.time,
                    value=val,
                )
                await ws.send_json(indicator_msg.model_dump())

            await asyncio.sleep(base_interval / speed)
    except WebSocketDisconnect:
        pass
