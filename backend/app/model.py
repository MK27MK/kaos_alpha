from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model with camelCase alias generation and validation."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
    )


class AddIndicatorRequest(CamelCaseModel):
    name: str
    parameters: dict[str, int | float]


class AddIndicatorResponse(CamelCaseModel):
    indicator_key: str


# class MarketFeatureModel(CamelCaseModel):
#     type: str
#     parameters: dict[str, int | str]
