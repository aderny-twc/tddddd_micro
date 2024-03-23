from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import date

from domain import model
from adapters import orm
from service_layer import services, unit_of_work

orm.start_mappers()
app = FastAPI()


class OrderLineModel(BaseModel):
    orderid: str
    sku: str
    qty: int


@app.post("/allocate", status_code=201)
def allocate_in_batch(order_line: OrderLineModel):
    uow = unit_of_work.SqlAlchemyUnitOfWork()

    try:
        batchref = services.allocate(order_line.orderid, order_line.sku, order_line.qty, uow)
    except (model.OutOfStock, services.InvalidSku) as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )

    return {"batchref": batchref}


class BatchModel(BaseModel):
    ref: str
    sku: str
    qty: int = Field(gt=0)
    eta: date | None = None


@app.post("/batch", status_code=201)
def add_batch(batch: BatchModel):
    uow = unit_of_work.SqlAlchemyUnitOfWork()

    services.add_batch(
        batch.ref, batch.sku, batch.qty, batch.eta, uow
    )

    return {"success": True}
