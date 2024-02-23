from datetime import date

from model import Batch, OrderLine


def _make_batch_and_line_with_qty(sku: str, batch_qty: int, line_qty: int) -> (Batch, OrderLine):
    return (
        Batch(ref="batch-001", sku=sku, qty=batch_qty, eta=date.today()),
        OrderLine(orderid="order-ref", sku=sku, qty=line_qty)
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = _make_batch_and_line_with_qty(sku="SMALL-TABLE", batch_qty=20, line_qty=2)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = _make_batch_and_line_with_qty("RED_TABLE", 10, 5)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = _make_batch_and_line_with_qty("RED_TABLE", 5, 10)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = _make_batch_and_line_with_qty("RED_TABLE", 5, 5)
    assert batch.can_allocate(line)


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = _make_batch_and_line_with_qty("RED_TABLE", 10, 5)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    batch, line = _make_batch_and_line_with_qty("SOME-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
