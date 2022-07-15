import os
from typing import Tuple, Union
from urllib.parse import urlparse
import textwrap
import stat
import getpass
from rich.panel import Panel
from rich import box
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

from sliceofml.display import Display

display = Display()


def _find_netrc_api_key(url, raise_errors=False):
    NETRC_FILES = (".netrc", "_netrc")
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        netrc_locations = (netrc_file,)
    else:
        netrc_locations = ("~/{}".format(f) for f in NETRC_FILES)

    try:
        from netrc import netrc, NetrcParseError

        netrc_path = None

        for f in netrc_locations:
            try:
                loc = os.path.expanduser(f)
            except KeyError:
                return

            if os.path.exists(loc):
                netrc_path = loc
                break

        if netrc_path is None:
            return

        ri = urlparse(url)

        host = ri.netloc.split(":")[0]

        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return (_netrc[login_i], _netrc[2])
        except (NetrcParseError, IOError):
            if raise_errors:
                raise

    except (ImportError, AttributeError):
        pass


REQUEST_TOKEN_URL = "https://api.twitter.com/oauth2/token"


def request_access_token(client_id: str, client_secret: str) -> str:
    """

    Get an access token for a given client_id and client_secret.

    Args:
        consumer_key (str):
            Your application consumer key.
        consumer_secret (str):
            Your application consumer secret.

    Returns:
        Bearer Token

    """
    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    try:
        token = oauth.fetch_token(token_url=REQUEST_TOKEN_URL, auth=auth)
        return token["access_token"]
    except Exception as err:
        display.error(f"{err}")
        raise ValueError(err)


DEVELOPER_DASHBOARD_URL = "https://developer.twitter.com/en/portal/dashboard"


def prompt_api_details() -> Tuple[str, str, str]:
    api_prompt = Panel(
        (
            "You can find your API keys :key: on your Twitter App Dashboard"
            f" [blue underline bold][link={DEVELOPER_DASHBOARD_URL}]here[/link][/blue underline bold] "
        ),
        box=box.ROUNDED,
    )
    display.log_styled(api_prompt, style="yellow")
    display.log(
        "Paste the Client ID, Secret and App Name from your profile and hit enter, or press ctrl+c to quit: "
    )
    client_id = getpass.getpass(prompt="Client ID 🆔 ")
    client_secret = getpass.getpass(prompt="Client Secret 🕵️ ")
    app_name = input("App Name ✏️  ")
    return (client_id, client_secret, app_name)


def read_credentials(api_url: str) -> Union[Tuple[str, str], None]:
    agent, token = None, None
    auth = _find_netrc_api_key(api_url, True)
    if auth and auth[0] and auth[1]:
        agent = auth[0]
        token = auth[1]
        return (agent, token)


def write_netrc(host: str, entity: str, key: str):
    normalized_host = urlparse(host).netloc.split(":")[0]
    if normalized_host != "localhost" and "." not in normalized_host:
        return None
    machine_line = "machine %s" % normalized_host
    path = os.path.expanduser("~/.netrc")
    orig_lines = None
    with open(path) as f:
        orig_lines = f.read().strip().split("\n")
    with open(path, "w") as f:
        if orig_lines:
            skip = 0
            for line in orig_lines:
                if line == "machine " or machine_line in line:
                    skip = 2
                elif skip:
                    skip -= 1
                else:
                    f.write("%s\n" % line)
        f.write(
            textwrap.dedent(
                """\
        machine {host}
          login {entity}
          password {key}
        """
            ).format(host=normalized_host, entity=entity, key=key)
        )
    os.chmod(os.path.expanduser("~/.netrc"), stat.S_IRUSR | stat.S_IWUSR)
    return True
