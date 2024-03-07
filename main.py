from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

import config
import model
import orm
import repository

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
    batches = repository.SqlAlchemyRepository(session).list()
    print("Batches: ", batches)
    line = model.OrderLine(
        orderid=order_line.orderid,
        sku=order_line.sku,
        qty=order_line.qty,
    )

    batchref = model.allocate(line, batches)

    return {"batchref": batchref}
