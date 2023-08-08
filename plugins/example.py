from utils.plugin import Plugin
from flask_classful import route
from utils.auth import requires_auth, requires_scope, require_scopes
from utils.exceptions import AuthError


class ExamplePlugin(Plugin):
    @property
    def name(self):
        return "example-plugin"

    @route('/<example_input>')
    def example_route(self, example_input):
        return f"Oh, hi {example_input}!"

    @requires_auth
    def example_auth(self):
        return f"Oh, hi! This private endpoint only requires authentication!"

    @requires_auth
    @requires_scope("example:pontoon")
    def example_scoped_auth(self):
        return f"Oh, hi! This endpoint is private and requires authentication and a specific scope!"

    @requires_auth
    @requires_scope("example:pontoon")
    def example_multi_scoped_auth(self):
        if require_scopes(["admin:pontoon"]):
            return f"Oh, hi! This endpoint is also private and requires authentication and two scopes!"
        raise AuthError({"code": "scope_missing",
                         "description": f"A required scope is missing. Scope: read:anything"}, 401)
