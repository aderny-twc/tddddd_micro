import redis
import json
from logging import getLogger

import config
from domain import commands
import bootstrap

logger = getLogger()

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus):
    logger.debug(f"handling {m}")
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(
        ref=data["batchref"],
        qty=data["qty"],
    )
    bus.handle(cmd)


if __name__ == "__main__":
    main()
