from adapters import redis_eventpublisher
from domain import model, events, commands
from service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def change_batch_quantity(command: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batchref(batchref=command.ref)
        product.change_batch_quantity(ref=command.ref, qty=command.qty)
        uow.commit()


def allocate(command: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(command.orderid, command.sku, command.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Wrong sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def add_batch(
        command: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    with uow:
        product = uow.products.get(sku=command.sku)
        if product is None:
            product = model.Product(command.sku, batches=[])
        uow.products.add(product)
        product.batches.append(model.Batch(command.ref, command.sku, command.qty, command.eta))
        uow.commit()


def publish_allocated_event(event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork):
    redis_eventpublisher.publish("line_allocated", event)


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
