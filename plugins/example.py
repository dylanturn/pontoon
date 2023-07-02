from flask import Blueprint

plugin = Blueprint(__name__, __name__)


@plugin.route('/<example_input>')
def example_route(example_input):
    return f"Oh, hi {example_input}!"
