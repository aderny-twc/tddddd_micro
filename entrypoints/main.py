from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

import bootstrap
from domain import commands
from entrypoints.schema import OrderLineModel, BatchModel
from service_layer import views
from service_layer.handlers import InvalidSku

app = FastAPI()
bus = bootstrap.bootstrap()


@app.post("/allocate", status_code=status.HTTP_201_CREATED)
def allocate_in_batch(order_line: OrderLineModel):
    try:
        command = commands.Allocate(
            order_line.orderid, order_line.sku, order_line.qty
        )
        bus.handle(command)
    except InvalidSku as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )

    return {"success": True}


@app.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def add_batch(batch: BatchModel):
    command = commands.CreateBatch(batch.ref, batch.sku, batch.qty, batch.eta)

    bus.handle(command)
    return {"success": True}


@app.get("/allocations/{orderid}", status_code=status.HTTP_200_OK)
def allocations_view_endpoint(orderid: str):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Not found"}
        )

    return result
