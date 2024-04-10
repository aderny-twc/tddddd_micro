from domain import events, commands
from logging import getLogger

from service_layer import unit_of_work
from service_layer import handlers

from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

logger = getLogger()

EVENT_HANDLERS: dict[type[events.Event], callable] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.Allocated: [
        handlers.publish_allocated_event,
        handlers.add_allocation_to_read_model,
    ],
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
            for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential()):
                with attempt:
                    logger.debug(f"handling event {event} with handler {handler}")
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            logger.error(f"Failed to process event {retry_failure.last_attempt.attempt_number} times")
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


class MessageBus:
    def __init__(
            self,
            uow: unit_of_work.AbstractUnitOfWork,
            event_handlers: dict[type[events.Event], list[callable]],
            command_handlers: dict[type[commands.Command], callable],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: commands.Command | events.Event):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} wa not in Event or Command")

    def handle_event(
            self,
            event: events.Event,
            queue: list,
    ):
        for handler in self.event_handlers[type(event)]:
            try:
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential()):
                    with attempt:
                        logger.debug(f"handling event {event} with handler {handler}")
                        handler(event)
                        queue.extend(self.uow.collect_new_events())
            except RetryError as retry_failure:
                logger.error(f"Failed to process event {retry_failure.last_attempt.attempt_number} times")
                continue

    def handle_command(
            self,
            command: commands.Command,
    ):
        logger.debug(f"handling command {command}")
        try:
            handler = self.command_handlers[type(command)]
            result = handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise