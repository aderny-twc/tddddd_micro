import pytest

from adapters import repository
from domain import events
from service_layer import unit_of_work, messagebus, handlers


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def commit(self):
        super().commit()

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()

    messagebus.handle(
        events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow
    )

    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()

    messagebus.handle(
        events.BatchCreated("b1", "GARISH-RUG", 100, None), uow
    )

    messagebus.handle(
        events.BatchCreated("b2", "GARISH-RUG", 99, None), uow
    )

    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()

    messagebus.handle(
        events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow
    )

    result = messagebus.handle(
        events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow
    )

    assert result == ["batch1"]


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    messagebus.handle(
        events.BatchCreated("b1", "AREALSKU", 100, None), uow
    )

    with pytest.raises(handlers.InvalidSku, match="Wrong sku NONEXISTENTSKU"):
        messagebus.handle(
            events.AllocationRequired("o1", "NONEXISTENTSKU", 10), uow
        )


def test_allocate_commits():
    uow = FakeUnitOfWork()
    messagebus.handle(
        events.BatchCreated("b1", "OMINOUS-MIRROR", 100, None), uow
    )
    messagebus.handle(
        events.AllocationRequired("o1", "OMINOUS-MIRROR", 10), uow
    )
    assert uow.committed
