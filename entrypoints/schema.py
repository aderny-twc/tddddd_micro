from pydantic import BaseModel, Field
from datetime import date


class OrderLineModel(BaseModel):
    orderid: str
    sku: str
    qty: int


class BatchModel(BaseModel):
    ref: str
    sku: str
    qty: int = Field(gt=0)
    eta: date | None = None
