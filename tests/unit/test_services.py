import pytest
from service_layer import services
from datetime import date, timedelta

from adapters.repository import FakeRepository
from service_layer import unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=2)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch_with_uow():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "SOME-LAMP", 100, None, uow)

    result = services.allocate("o1", "SOME-LAMP", 10, uow)
    assert result == "b1"


# def test_add_batch():
#     uow = FakeUnitOfWork()
#
#     services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
#
#     assert repo.get("b1") is not None
#     assert session.committed


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "SOME-LAMP", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Wrong sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)

    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)
    assert uow.committed is True
