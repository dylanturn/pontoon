from flask import Blueprint

plugin = Blueprint(__name__, __name__)


class PluginHealth:
    def __init__(self, *loaded_plugin):
      self.loaded_plugins = loaded_plugin


@plugin.route('/alive')
def alive_route():
    return "I'm alive, I promise!"


@plugin.route('/ready')
def ready_route():
    return "I'm ready, I promise!"
