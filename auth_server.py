"""Serveur d'authentification (login / login_ex)."""
import logging

from nintendo.nex import authentication, common, rmc

import config
import users
from tickets import generate_ticket

log = logging.getLogger("auth")


class AuthenticationServer(authentication.AuthenticationServer):
    def __init__(self, nex_settings):
        super().__init__()
        self.settings = nex_settings

    async def login(self, client, username):
        log.info("login: %s", username)
        user = users.get_by_name(username)
        if user is None:
            raise common.RMCError("RendezVous::InvalidUsername")
        return self._response(user)

    async def login_ex(self, client, username, extra_data):
        # Sur Wii U, extra_data contient un token du serveur de comptes.
        # Il n'est pas vérifié ici : à implémenter pour un vrai serveur.
        log.info("login_ex: %s", username)
        user = users.get_by_name(username)
        if user is None and config.DEV_MODE:
            log.warning("Utilisateur inconnu '%s', repli sur guest", username)
            user = users.get_by_name("guest")
        if user is None:
            raise common.RMCError("RendezVous::InvalidUsername")
        return self._response(user)

    def _response(self, user):
        server = users.secure_server_user()

        url = common.StationURL(
            scheme="prudps", address=config.HOST, port=config.SECURE_PORT,
            PID=server.pid, CID=1, type=2, sid=1, stream=10,
        )

        conn_data = authentication.RVConnectionData()
        conn_data.main_station = url
        conn_data.special_protocols = []
        conn_data.special_station = common.StationURL()

        response = rmc.RMCResponse()
        response.result = common.Result.success()
        response.pid = user.pid
        response.ticket = generate_ticket(self.settings, user, server)
        response.connection_data = conn_data
        response.server_name = config.SERVER_NAME
        return response
