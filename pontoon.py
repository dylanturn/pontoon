import os
import logging
from flask import Flask, jsonify
from utils import health
from utils import plugin
from utils.exceptions import AuthError


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


if __name__ == "__main__":
  pontoon_host = os.environ.get('PONTOON_HOST')
  pontoon_port = int(os.environ.get('PONTOON_PORT'))
  pontoon_ssl = os.environ.get('PONTOON_SSL')
  pontoon_cert = os.environ.get('PONTOON_CERT', None)
  pontoon_key = os.environ.get('PONTOON_KEY', None)
  # TODO: Implement this
  # pontoon_auth = os.environ.get('PONTOON_AUTH')

  pontoon_ssl_context = None

  if pontoon_ssl.lower() != "false":
    if (pontoon_cert is None) or (pontoon_key is None):
      print("Starting with adhoc SSL")
      pontoon_ssl_context = 'adhoc'
    else:
      print("Starting with provided SSL certs.")
      pontoon_ssl_context = (pontoon_cert, pontoon_key)
  else:
    print("Starting without SSL")

  plugin_loader = plugin.PluginLoader(app, "/api/v1")
  plugin_health = health.PluginHealth(plugin_loader.loaded_plugins)

  print("====================")
  print("Routes Loaded:")
  for rule in app.url_map._rules:
    print(f"\t{rule}")
  print("====================")

  app.run(host=pontoon_host, port=pontoon_port, ssl_context=pontoon_ssl_context)
