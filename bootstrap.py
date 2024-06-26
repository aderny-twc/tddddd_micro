import inspect

from adapters import redis_eventpublisher, orm
from service_layer import unit_of_work, messagebus


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
    # send_mail: callable = email.send
    publish: callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()

    dependencies = {"uow": uow, "publish": publish}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in messagebus.EVENT_HANDLERS.items()
    }

    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in messagebus.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }

    return lambda message: handler(message, **deps)
