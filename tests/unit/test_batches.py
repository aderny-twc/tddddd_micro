from datetime import date, timedelta
import pytest

from src.allocation.domain.model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


@pytest.skip(msg="Later")
def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch-002", "PILLOW-BLUE", qty=1, eta=date.today())
    line = OrderLine("order-ref", "PILLOW-BLUE", 2)

    batch.allocate(line)

    assert batch.available_quantity >= 0


@pytest.skip(msg="Later")
def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-003", "VASE-BLUE", qty=10, eta=date.today())
    line = OrderLine("order-ref", "VASE-BLUE", 2)
    line2 = OrderLine("order-ref", "VASE-BLUE", 2)

    batch.allocate(line)
    batch.allocate(line2)

    assert batch.available_quantity == 8


@pytest.skip(msg="Later")
def test_can_allocate_if_available_equal_to_required():
    pytest.fail("todo")


@pytest.skip(msg="Later")
def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


@pytest.skip(msg="Later")
def test_prefers_earlier_batches():
    pytest.fail("todo")
