from domain import model
from adapters.repository import AbstractRepository
from typing import Any
from datetime import date


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, repo: AbstractRepository, session: Any) -> str:
    batches = repo.list()

    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Wrong sku {sku}")

    line = model.OrderLine(order_id, sku, qty)

    batchref = model.allocate(line, batches)
    session.commit()

    return batchref


def add_batch(
        ref: str, sku: str, qty: int, eta: date | None, repo: AbstractRepository, session: Any
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()
