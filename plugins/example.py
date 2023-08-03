from utils.plugin import Plugin
from flask_classful import route
from utils.authentication import login_required


class ExamplePlugin(Plugin):
    @property
    def name(self):
        return "example-plugin"

    @route('/<example_input>')
    def example_route(self, example_input):
        return f"Oh, hi {example_input}!"

    @login_required
    def example_two(self):
        return f"Oh, hi !"