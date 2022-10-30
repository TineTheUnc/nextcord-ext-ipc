import logging

from .errors import *
import websockets
import json

log = logging.getLogger(__name__)


class Client:
    """
    Handles webserver side requests to the bot process.

    Parameters
    ----------
    host: str
        The IP or host of the IPC server, defaults to localhost
    port: int
        The port of the IPC server. If not supplied the port will be found automatically, defaults to None
    secret_key: Union[str, bytes]
        The secret key for your IPC server. Must match the server secret_key or requests will not go ahead, defaults to None
    """

    def __init__(self, host="localhost", port=None, secret_key=None, ssl_mode=False, use_port=True):
        """Constructor"""

        self.secret_key = secret_key

        self.host = host
        self.port = port
        self.ssl_mode = ssl_mode
        self.use_port = use_port


        self.websocket = None


    @property
    def url(self):
        if self.use_port:
            return "{0}://{1}:{2}".format("wss" if self.ssl_mode else "ws",self.host, self.port )
        else:
            return "{0}://{1}".format("wss" if self.ssl_mode else "ws",self.host)

    async def request(self, endpoint, **kwargs):
        """Make a request to the IPC server process.

        Parameters
        ----------
        endpoint: str
            The endpoint to request on the server
        **kwargs
            The data to send to the endpoint
        """
        log.info("Requesting IPC Server for %r with %r", endpoint, kwargs)

        payload = {
            "endpoint": endpoint,
            "data": kwargs,
            "headers": {"Authorization": self.secret_key},
        }
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(payload))

            log.debug("Client > %r", payload)

            recv = await websocket.recv()

            log.debug("Client < %r", recv)

            return recv.json()
