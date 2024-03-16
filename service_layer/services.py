from domain import model
from datetime import date
from service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f"Wrong sku {sku}")

        line = model.OrderLine(order_id, sku, qty)
        batchref = model.allocate(line, batches)
        uow.commit()

    return batchref


def add_batch(
        ref: str, sku: str, qty: int, eta: date | None, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
