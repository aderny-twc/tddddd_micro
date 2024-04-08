import redis
import json
from logging import getLogger

import config
from domain import commands
from service_layer import messagebus, unit_of_work
from adapters import orm

logger = getLogger()

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logger.debug(f"handling {m}")
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(
        ref=data["batchref"],
        qty=data["qty"],
    )
    messagebus.handle(cmd, uow=unit_of_work.SqlAlchemyUnitOfWork())


if __name__ == "__main__":
    main()