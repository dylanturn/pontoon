import os
import sys
import pkgutil
from flask import Flask
from utils import health


def load_plugins():
  print("Start loading plugins...")
  for importer, package_name, _ in pkgutil.iter_modules(["plugins"]):
    full_package_name = '%s.%s' % ("plugins", package_name)
    if full_package_name not in sys.modules:
      module = importer.find_module(package_name).load_module(package_name)
      print(f"Loading plugin: {module.__name__}")
      app.register_blueprint(module.plugin, url_prefix=f"/api/v1/{module.__name__}")
  print("Plugin loading complete!")
  print(app.url_map)


app = Flask(__name__)
load_plugins()
app.register_blueprint(health.plugin, url_prefix=f"/api/v1/health")


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

  app.run(host=pontoon_host, port=pontoon_port, ssl_context=pontoon_ssl_context)
