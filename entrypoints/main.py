from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from domain import commands
from adapters import orm
from entrypoints.schema import OrderLineModel, BatchModel
from service_layer import handlers, unit_of_work, messagebus, views

orm.start_mappers()
app = FastAPI()


@app.post("/allocate", status_code=status.HTTP_202_ACCEPTED)
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


@app.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def add_batch(batch: BatchModel):
    command = commands.CreateBatch(
        batch.ref, batch.sku, batch.qty, batch.eta
    )

    messagebus.handle(
        command,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )

    return {"success": True}


@app.get("/allocations/{orderid}")
def allocations_view_endpoint(orderid: str):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Not found"}
        )

    return result
