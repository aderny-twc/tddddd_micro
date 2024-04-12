import pytest

import bootstrap
from adapters import repository
from domain import events, commands
from service_layer import unit_of_work, messagebus, handlers
from datetime import date


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next((
            p for p in self._products for b in p.batches
            if b.reference == batchref
        ), None)


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


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        publish=lambda *args: None,
    )


def test_add_batch_for_new_product():
    bus = bootstrap_test_app()
    bus.handle(commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None))

    assert bus.uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert bus.uow.committed


def test_add_batch_for_existing_product():
    bus = bootstrap_test_app()

    bus.handle(commands.CreateBatch("b1", "GARISH-RUG", 100, None))
    bus.handle(commands.CreateBatch("b2", "GARISH-RUG", 99, None))

    assert "b2" in [b.reference for b in bus.uow.products.get("GARISH-RUG").batches]


def test_errors_for_invalid_sku():
    bus = bootstrap_test_app()
    bus.handle(commands.CreateBatch("b1", "AREALSKU", 100, None))

    with pytest.raises(handlers.InvalidSku, match="Wrong sku NONEXISTENTSKU"):
        bus.handle(commands.Allocate("o1", "NONEXISTENTSKU", 10))


def test_allocate_commits():
    bus = bootstrap_test_app()
    bus.handle(commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None))
    bus.handle(commands.Allocate("o1", "OMINOUS-MIRROR", 10))
    assert bus.uow.committed


def test_changes_available_quantity():
    bus = bootstrap_test_app()
    bus.handle(commands.CreateBatch("b1", "SUPER-CLEAN-MIRROR", 100, None))
    [batch] = bus.uow.products.get(sku="SUPER-CLEAN-MIRROR").batches

    assert batch.available_quantity == 100

    bus.handle(commands.ChangeBatchQuantity("b1", 50))

    assert batch.available_quantity == 50


def test_reallocates_if_necessary():
    bus = bootstrap_test_app()
    history = [
        commands.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
        commands.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
        commands.Allocate("order1", "INDIFFERENT-TABLE", 20),
        commands.Allocate("order2", "INDIFFERENT-TABLE", 20),
    ]
    for msg in history:
        bus.handle(msg)
    [batch1, batch2] = bus.uow.products.get(sku="INDIFFERENT-TABLE").batches
    assert batch1.available_quantity == 10
    assert batch2.available_quantity == 50

    bus.handle(commands.ChangeBatchQuantity("batch1", 25))

    # order1 or order2 will be deallocated, so we'll have 25 - 20
    assert batch1.available_quantity == 5
    # and 20 will be reallocated to the next batch
    assert batch2.available_quantity == 30
