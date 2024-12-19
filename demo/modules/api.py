import requests
from . import auth
import json
from .logging import configure_logger
from .helpers import output_endpoint_error

class EndpointException(Exception):
    pass


def call_endpoint_base(method, name, payload=None):
    if payload is None:
        payload = {}
    response = requests.request(
        method,
        "{}://{}:{}/api/{}/".format(auth.protocol, auth.host, auth.port, name),
        headers={
            "Authorization": "Bearer {}".format(auth.access_token),
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        proxies=auth.proxies,
    )
    return response


def call_endpoint_silent(method, name, payload=None):
    response = call_endpoint_base(method, name, payload)
    if not response.ok:
        raise EndpointException(response.text)
    return response


def call_endpoint(method, name, payload=None):
    response = call_endpoint_base(method, name, payload)
    if not response.ok:
        output_endpoint_error(response.text)
        raise EndpointException("Critical endpoint exception, see the html file")
    return response


def get_access_token(username, password):
    response = call_endpoint(
        "POST", "token", {"username": username, "password": password}
    )
    access_token = json.loads(response.text)["access"]
    return access_token
