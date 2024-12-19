from modules.logging import configure_logger

access_token = ""
protocol = ""
host = ""
port = ""
# protocol = 'https'
# host = 'deft.ikimio.com'
# port = '443'
proxies = {
    #   'http': 'proxy.sig.umbrella.com:80',
    #   'https': 'proxy.sig.umbrella.com:443',
}

def setup_auth(config):
    global access_token, protocol, host, port
    protocol = config.get("protocol", "http")
    host = config.get("host", "localhost")
    port = config.get("port", "8000")

    from .api import get_access_token

    logger = configure_logger()
    logger.info("Getting access token")
    access_token = get_access_token(config.get("username"), config.get("password"))
    logger.info(f"Access token: {access_token}")
