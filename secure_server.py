"""Serveur sécurisé : enregistrement de la connexion du client."""
import logging

from nintendo.nex import common, rmc, secure

log = logging.getLogger("secure")


class SecureConnectionServer(secure.SecureConnectionServer):
    def __init__(self):
        super().__init__()
        self._next_cid = 1

    async def register(self, client, urls):
        cid = self._next_cid
        self._next_cid += 1

        addr = client.remote_address()
        log.info("register: pid=%s cid=%s addr=%s", client.pid(), cid, addr)

        url = common.StationURL(
            scheme="prudp", address=addr[0], port=addr[1],
            PID=client.pid(), CID=cid, type=2, sid=1, stream=10,
        )

        response = rmc.RMCResponse()
        response.result = common.Result.success()
        response.connection_id = cid
        response.public_station = url
        return response
