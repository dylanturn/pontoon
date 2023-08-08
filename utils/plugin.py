import os
import sys
import time
import signal
import logging
import pkgutil
from utils.cache import RedisCache
from flask_classful import FlaskView
from jinja2 import Environment, PackageLoader, select_autoescape

log = logging.getLogger(__name__)


class Plugin(FlaskView):

  method_dashified = True
  excluded_methods = [
    '__init__',
    'name',
    'cache_client',
    'alive',
    'ready',
    'on_startup',
    'on_shutdown'
  ]

  def __init__(self):
    self.on_startup()
    self.redis_client = RedisCache(self.__class__.__name__, os.environ['REDIS_HOST'], os.environ['REDIS_PORT'], os.environ['REDIS_DB'])
#    self.env = Environment(
#      loader=PackageLoader(self.name),
#      autoescape=select_autoescape()
#    )

  @property
  def name(self):
    return self.__class__.__name__

  @property
  def cache_client(self) -> RedisCache:
    return self.redis_client

  @property
  def alive(self) -> bool:
    return True

  @property
  def ready(self) -> bool:
    return True

  def on_startup(self):
    pass

  def on_shutdown(self):
    pass


class PluginLoader:

  def __init__(self, app, base_path: str):

    signal.signal(signal.SIGINT, self._on_shutdown)
    signal.signal(signal.SIGTERM, self._on_shutdown)

    self.loaded_plugins = []
    self.app = app
    self.base_path = base_path

    self.app.secret_key = "super secret key"

    log.info("Start loading plugins...")

    for importer, package_name, _ in pkgutil.iter_modules(["plugins"]):
      full_package_name = '%s.%s' % ("plugins", package_name)
      if full_package_name not in sys.modules:
        importer.find_module(package_name).load_module(package_name)

    for plugin_class in Plugin.__subclasses__():
      self.loaded_plugins.append(self._load(plugin_class))

    log.info("Plugin loading complete!")

  def _load(self, plugin_class: Plugin.__class__) -> any:
    log.info(f"Loading plugin: {plugin_class.__name__}")

    plugin_instance = plugin_class()
    while not plugin_instance.ready or not plugin_instance.alive:
      time.sleep(5)

    plugin_instance.register(self.app, trailing_slash=False, route_base=f"{self.base_path}/{plugin_instance.name.lower()}")
    log.info("Plugin loaded!")
    self.loaded_plugins.append(plugin_instance)

  def _on_shutdown(self):
    for loaded_plugin in self.loaded_plugins:
      loaded_plugin.on_shutdown()
