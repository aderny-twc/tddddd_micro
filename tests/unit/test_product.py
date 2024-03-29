from domain import events
from domain.model import Batch, Product, OrderLine


def test_records_out_of_stock_event_if_cannot_allocate():
    sku = "SMALL-CHAIR"
    batch = Batch("batch1", sku, 10, eta=None)
    product = Product(sku=sku, batches=[batch])
    product.allocate(OrderLine("order1", sku, 10))

    allocation = product.allocate(OrderLine("order2", sku, 1))
    assert product.events[-1] == events.OutOfStock(sku=sku)
    assert allocation is None
