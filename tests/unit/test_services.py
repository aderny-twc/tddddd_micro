from domain import model
import pytest
from service_layer import services
from datetime import date, timedelta

from adapters.repository import FakeRepository

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=2)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "SOME-LAMP", 100, None, repo, session)

    result = services.allocate("o1", "SOME-LAMP", 10, repo, FakeSession())
    assert result == "b1"


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)

    assert repo.get("b1") is not None
    assert session.committed


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "SOME-LAMP", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Wrong sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, repo, session)

    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)
    assert session.committed is True
