from typing import Literal

from pydantic import BaseModel

from app.data_model.camel_case_model import CamelCaseModel

type IndicatorParameters = dict[str, int | float | str]


class AddIndicatorRequest(CamelCaseModel):
    name: str
    parameters: IndicatorParameters


class AddIndicatorResponse(CamelCaseModel):
    indicator_key: str


# class MarketFeatureModel(CamelCaseModel):
#     type: str
#     parameters: dict[str, int | str]

# ws - server -> client ------------------------------------------------


class PriceMessage(BaseModel):
    type: Literal["price"] = "price"
    time: int
    value: float


class IndicatorMessage(BaseModel):
    type: Literal["indicator"] = "indicator"
    key: str
    time: int
    value: float | dict[str, float]


# ws - client -> server ------------------------------------------------


class ControlMessage(BaseModel):
    type: Literal["control"] = "control"
    action: Literal["pause", "resume", "reset", "speed"]
    value: float | None = None
