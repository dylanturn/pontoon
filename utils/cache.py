import os
import json
import redis
import logging
import base64
import inspect

log = logging.getLogger(__name__)


class RedisCache:
  def __init__(self, plugin_name, redis_host, redis_port, redis_db, redis_user=None, redis_pass=None):
    self.plugin_name = plugin_name
    self.default_cache_ttl = os.environ.get('PONTOON_DEFAULT_CACHE_TTL', 259200)
    if (redis_user is None) or (redis_pass is None):
      self.client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    else:
      self.client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, username=redis_user, password=redis_pass)

  def cache_item(self, item_key, item_value, item_ttl=None):

    # Get the value type so we know what we're dealing with.
    item_format = type(item_value).__name__

    # Create the item entry object that encapsulates the value.
    item_entry = dict()
    item_entry["format"] = item_format
    log.info(f"Payload format: {item_format}")

    # If the value is a JSON object we need to dump it to a string first.
    if (item_format is dict.__name__) or (item_format is list.__name__):
      item_entry["value"] = json.dumps(item_value)
    else:
      item_entry["value"] = item_value

    # Figure out how long we should retain this cache entry for.
    if item_ttl is None:
      item_ttl = self.default_cache_ttl

    log.info(f"Set item with key: {self.plugin_name}:{item_key}")
    # place the entry into Redis with the appropriate TTL.
    self.client.set(f"{self.plugin_name}:{item_key}", json.dumps(item_entry), ex=item_ttl)

  def get_cache_item(self, item_key):
    log.info(f" {inspect.stack()[1][3]}-Get item with key: {self.plugin_name}:{item_key}")

    # Go to Redis to get the cache entry
    cache_entry = self.client.get(f"{self.plugin_name}:{item_key}")

    # If the cache entry is None we just return None.
    if cache_entry is None:
      return None

    # Load the entry into a json object.
    cache_entry = json.loads(cache_entry)

    # If the format is list or dict then we need to load up the value into a JSON object
    if (cache_entry["format"] is dict.__name__) or (cache_entry["format"] is list.__name__):
      return json.loads(cache_entry["value"])
    else:
      return cache_entry["value"]

  def expire_cache_item(self, item_key):
    log.info(f"Expire item with key: {self.plugin_name}:{item_key}")
    self.client.delete(f"{self.plugin_name}:{item_key}")
