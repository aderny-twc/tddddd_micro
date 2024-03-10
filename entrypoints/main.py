from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

import config
from domain import model
from adapters import orm, repository
from service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = FastAPI()


class OrderLineModel(BaseModel):
    orderid: str
    sku: str
    qty: int


@app.post("/allocate/", status_code=201)
def allocate_in_batch(order_line: OrderLineModel):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    try:
        batchref = services.allocate(order_line.orderid, order_line.sku, order_line.qty, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": str(e)}
            )

    return {"batchref": batchref}
