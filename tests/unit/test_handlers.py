import pytest

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


# example of fake uow with messagebus
class FakeUnitOfWorkWithFakeMessageBus(FakeUnitOfWork):
    def __init__(self):
        super().__init__()
        self.events_published: list[events.Event] = []

    def publish_events(self):
        print("Are we here?")
        for product in self.products.seen:
            while product.events:
                self.events_published.append(product.events.pop(0))


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()

    messagebus.handle(
        commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None), uow
    )

    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()

    messagebus.handle(
        commands.CreateBatch("b1", "GARISH-RUG", 100, None), uow
    )

    messagebus.handle(
        commands.CreateBatch("b2", "GARISH-RUG", 99, None), uow
    )

    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()

    messagebus.handle(
        commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None), uow
    )

    result = messagebus.handle(
        commands.Allocate("o1", "COMPLICATED-LAMP", 10), uow
    )

    assert result == ["batch1"]


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    messagebus.handle(
        commands.CreateBatch("b1", "AREALSKU", 100, None), uow
    )

    with pytest.raises(handlers.InvalidSku, match="Wrong sku NONEXISTENTSKU"):
        messagebus.handle(
            commands.Allocate("o1", "NONEXISTENTSKU", 10), uow
        )


def test_allocate_commits():
    uow = FakeUnitOfWork()
    messagebus.handle(
        commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None), uow
    )
    messagebus.handle(
        commands.Allocate("o1", "OMINOUS-MIRROR", 10), uow
    )
    assert uow.committed


def test_changes_available_quantity():
    uow = FakeUnitOfWork()
    messagebus.handle(
        commands.CreateBatch("b1", "SUPER-CLEAN-MIRROR", 100, None), uow
    )
    [batch] = uow.products.get(sku="SUPER-CLEAN-MIRROR").batches
    assert batch.available_quantity == 100

    messagebus.handle(
        commands.ChangeBatchQuantity("b1", 50), uow
    )

    assert batch.available_quantity == 50


def test_reallocates_if_necessary():
    uow = FakeUnitOfWork()
    command_history = [
        commands.CreateBatch("batch1", "REALLY-RED-CHAIR", 50, None),
        commands.CreateBatch("batch2", "REALLY-RED-CHAIR", 50, date.today()),
        commands.Allocate("order1", "REALLY-RED-CHAIR", 20),
        commands.Allocate("order2", "REALLY-RED-CHAIR", 20),
    ]
    for command in command_history:
        messagebus.handle(command, uow)
    [batch1, batch2] = uow.products.get(sku="REALLY-RED-CHAIR").batches

    assert batch1.available_quantity == 10
    assert batch2.available_quantity == 50

    messagebus.handle(commands.ChangeBatchQuantity("batch1", 25), uow)

    # allocations order1 or order2 will be rejected, we have 25 - 20
    assert batch1.available_quantity == 5
    # second order allocated in batch2
    assert batch2.available_quantity == 30
