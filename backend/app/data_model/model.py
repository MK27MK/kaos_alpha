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
