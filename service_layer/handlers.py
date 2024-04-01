from domain import model, events
from datetime import date
from service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(event: events.AllocationRequired, uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Wrong sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def add_batch(
        event: events.BatchCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
        uow.products.add(product)
        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()


def send_out_of_stock_notification(event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork):
    email_sender = FakeEmailSender()
    email_sender.send_mail(
        "stock@made.com",
        f"SKU {event.sku} out of stock",
    )


class FakeEmailSender:
    @staticmethod
    def send_mail(address: str, message: str) -> None:
        print("Send message to: ", address, ". Message: ", message)
