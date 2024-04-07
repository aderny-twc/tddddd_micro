import redis
import json
import config
from logging import getLogger
from dataclasses import asdict
from domain import events

logger = getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: events.Event):
    logger.debug(f"publishing: channel={channel}, event={event}")
    r.publish(channel, json.dumps(asdict(event)))
