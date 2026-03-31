"""Centralized indicator schema definitions.

Single source of truth for indicator metadata: parameter names, types,
constraints, defaults, UI hints, and key generation.
The frontend fetches these via GET /api/indicator-schemas.
"""

from typing import Literal

from app.data_model.camel_case_model import CamelCaseModel

type IndicatorKey = str


class OptionSchema(CamelCaseModel):
    name: str
    display_name: str


class ParameterSchema(CamelCaseModel):
    name: str
    display_name: str
    html_tag: Literal["input", "select"]
    # If true, this param is part of the indicator key (used for deduplication).
    # If false, it's condition-specific (e.g. band, shift) and excluded from the key.
    plot_param: bool
    min: float | None = None
    max: float | None = None
    default: float | str
    options: list[OptionSchema] | None = None


class IndicatorSchema(CamelCaseModel):
    name: str
    display_name: str
    parameters: list[ParameterSchema]


INDICATOR_SCHEMAS: dict[str, IndicatorSchema] = {
    "price": IndicatorSchema(
        name="price",
        display_name="Price",
        parameters=[
            ParameterSchema(
                name="shift",
                display_name="Shift",
                html_tag="input",
                plot_param=False,
                min=0,
                max=100,
                default=0,
            ),
        ],
    ),
    "hour": IndicatorSchema(
        name="hour",
        display_name="Hour",
        parameters=[
            ParameterSchema(
                name="shift",
                display_name="Shift",
                html_tag="input",
                plot_param=False,
                min=0,
                max=100,
                default=0,
            ),
        ],
    ),
    "sma": IndicatorSchema(
        name="sma",
        display_name="SMA",
        parameters=[
            ParameterSchema(
                name="length",
                display_name="Length",
                html_tag="input",
                plot_param=True,
                min=1,
                max=200,
                default=20,
            ),
        ],
    ),
    "bollinger_bands": IndicatorSchema(
        name="bollinger_bands",
        display_name="Bollinger Bands",
        parameters=[
            ParameterSchema(
                name="band",
                display_name="Band",
                html_tag="select",
                plot_param=False,
                default="upper",
                options=[
                    OptionSchema(name="upper", display_name="Upper"),
                    OptionSchema(name="lower", display_name="Lower"),
                ],
            ),
            ParameterSchema(
                name="length",
                display_name="Length",
                html_tag="input",
                plot_param=True,
                min=1,
                max=200,
                default=20,
            ),
            ParameterSchema(
                name="std_dev",
                display_name="StDev",
                html_tag="input",
                plot_param=True,
                min=1,
                max=5,
                default=2,
            ),
        ],
    ),
}
