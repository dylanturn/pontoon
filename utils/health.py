from flask import Blueprint

plugin = Blueprint(__name__, __name__)


@plugin.route('/alive')
def alive_route():
    return "I'm alive, I promise!"

@plugin.route('/ready')
def ready_route():
    return "I'm ready, I promise!"
