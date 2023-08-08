from flask import request, _request_ctx_stack
from functools import wraps
from utils.exceptions import AuthError
from six.moves.urllib.request import urlopen
import json
import os
from jose import jwt


AUTH0_DOMAIN = os.getenv("OIDC_DOMAIN")
API_AUDIENCE = os.getenv("OIDC_API_AUDIENCE")
ALGORITHMS = [os.getenv("OIDC_ALGORITHM")]


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        print(f"token: {token}")
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )

                print(payload)
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


def require_scopes(required_scopes):
  """Determines if a set of required scopes are present in the Access Token
  Args:
      required_scopes (Set(str)): A set of scopes required to access the resource
  """

  def contains_scope(required_scope):
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
      token_scopes = unverified_claims["scope"].split()
      for token_scope in token_scopes:
        if token_scope == required_scope:
          return True
    return False

  for scope in required_scopes:
    if not contains_scope(scope):
      return False
  return True


def requires_scope(required_scope):
  """Used as a decorator to determine if the required scope is present in the Access Token
  Args:
      required_scope (str): The scope required to access the resource
  """
  def decorator(f):
    def wrapper(*args, **kwargs):
      if require_scopes([required_scope]):
        return f(*args, **kwargs)
      raise AuthError({"code": "scope_missing", "description": f"A required scope is missing. {required_scope}"}, 401)
    return wrapper
  return decorator
