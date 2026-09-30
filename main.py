"""Point d'entrée : py main.py"""
import asyncio
import logging

import aioconsole
from nintendo.nex import rmc, settings

import config
import users
from auth_server import AuthenticationServer
from secure_server import SecureConnectionServer
from tickets import derive_key

logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


async def main():
    nex_settings = settings.load(config.SETTINGS_PROFILE)
    nex_settings.configure(config.ACCESS_KEY, config.NEX_VERSION)

    auth_servers = [AuthenticationServer(nex_settings)]
    secure_servers = [SecureConnectionServer()]

    secure_key = derive_key(users.secure_server_user())

    log.info("Adresse annoncée : %s (auth:%d, secure:%d)",
             config.HOST, config.AUTH_PORT, config.SECURE_PORT)

    async with rmc.serve(nex_settings, auth_servers, config.BIND, config.AUTH_PORT):
        async with rmc.serve(nex_settings, secure_servers, config.BIND,
                             config.SECURE_PORT, key=secure_key):
            await aioconsole.ainput("Appuie sur Entrée pour quitter...\n")

    log.info("Serveur arrêté")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
