from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import date

from domain import commands
from adapters import orm
from service_layer import handlers, unit_of_work, messagebus

orm.start_mappers()
app = FastAPI()


class OrderLineModel(BaseModel):
    orderid: str
    sku: str
    qty: int


class BatchModel(BaseModel):
    ref: str
    sku: str
    qty: int = Field(gt=0)
    eta: date | None = None


@app.post("/allocate", status_code=201)
def allocate_in_batch(order_line: OrderLineModel):
    try:
        command = commands.Allocate(
            order_line.orderid, order_line.sku, order_line.qty
        )
        results = messagebus.handle(
            command,
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except handlers.InvalidSku as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )

    return {"batchref": results[0]}


@app.post("/batch", status_code=201)
def add_batch(batch: BatchModel):
    command = commands.CreateBatch(
        batch.ref, batch.sku, batch.qty, batch.eta
    )

    messagebus.handle(
        command,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )

    return {"success": True}
