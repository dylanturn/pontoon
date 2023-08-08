import uuid
from urllib.parse import urlencode, quote_plus
from jinja2 import Environment, PackageLoader, select_autoescape
from utils.plugin import Plugin
from flask_classful import route
from authlib.integrations.flask_client import OAuth
from flask import Flask, request, redirect, render_template, session, url_for
import json
import dill


class WhoAmI(Plugin):

    @property
    def name(self):
        return "whoami"

    @route('/')
    def whoami(self):
      return render_template("whoami.html", session=session.get('user'),
                             pretty=json.dumps(session.get('user'), indent=4))
#      env = Environment(
#        loader=PackageLoader("yourapp"),
#        autoescape=select_autoescape()
#      )
#      return template.render(the="variables", go="here")
#      template = env.get_template("whoami.html")


    @route('/lookup', methods=['POST'])
    def lookup(self):

      request_id = f"{uuid.uuid1()}"

      payload = request.form
      client_id = payload["client_id"]
      client_secret = payload["client_secret"]
      scope = payload["scope"]
      server_metadata_url = payload["server_metadata_url"]

      #self.cache_client.cache_item(f"{request_id}:api_base_url", payload["server_metadata_url"])

      app = Flask("whoami")
      app.secret_key = request_id

      oauth = OAuth(app)
      oauth.register(
        "oidc",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={
          "scope": scope,
        },
        server_metadata_url=server_metadata_url
      )

      self.cache_client.cache_item(request_id, dill.dumps(oauth.oidc, recurse=True).decode("ISO-8859-1"), item_ttl=300)
      return oauth.oidc.authorize_redirect(
        redirect_uri=f"http://127.0.0.1:5000/api/v1/whoami/callback?requestId={request_id}"
      )

    @route("/callback", methods=["GET", "POST"])
    def callback(self):
      oidc = dill.loads(bytes(self.cache_client.get_cache_item(request.args.get('requestId')), 'ISO-8859-1'))

      try:
        token = oidc.authorize_access_token()
        session["user"] = token
        print(session["user"])

      except Exception as err:
        print(f"Failed to get token: {err}")
        session.clear()
        return self.callback()

      return oidc.authorize_redirect(
        redirect_uri=f"http://127.0.0.1:5000/api/v1/whoami?requestId={request.args.get('requestId')}"
      )

    @route("/logout", methods=["GET"])
    def logout(self):
      auth_base_url = session["user"]["userinfo"]["iss"]
      session.clear()
      return redirect(
        f"{auth_base_url}v2/logout?"
        + urlencode({"returnTo": url_for("WhoAmI:whoami", _external=True)},quote_via=quote_plus,)
      )
