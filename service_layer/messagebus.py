from domain import events, commands
from logging import getLogger

from service_layer import unit_of_work
from service_layer import handlers

logger = getLogger()

EVENT_HANDLERS: dict[type[events.Event], callable] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS: dict[type[commands.Command], callable] = {
    commands.CreateBatch: handlers.add_batch,
    commands.Allocate: handlers.allocate,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}


def handle(
    message: commands.Command | events.Event,
    uow: unit_of_work.AbstractUnitOfWork
):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} wa not in Event or Command")

    return results


def handle_event(
    event: events.Event,
    queue: list,
    uow: unit_of_work.AbstractUnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug(f"handling event {event} with handler {handler}")
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception(f"Exception handling event {event}")
            continue


def handle_command(
    command: commands.Command,
    queue: list,
    uow: unit_of_work.AbstractUnitOfWork,
):
    logger.debug(f"handling command {command}")
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception(f"Exception handling command {command}")
        raise
