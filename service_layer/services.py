from domain import model
from datetime import date
from service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(order_id, sku, qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Wrong sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def add_batch(
        ref: str, sku: str, qty: int, eta: date | None, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
        uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()
