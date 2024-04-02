from domain import events
from typing import Callable

from service_layer import unit_of_work
from service_layer import handlers


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    # Initiate queue with first event
    queue = [event]
    results = []
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            # collect all new events and append to queue
            queue.extend(uow.collect_new_events())
    return results


HANDLERS: dict[type[events.Event], list[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.BatchCreated: [handlers.add_batch],
    events.AllocationRequired: [handlers.allocate],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
}
