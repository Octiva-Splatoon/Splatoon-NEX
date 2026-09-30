from nintendo.nex import rmc, kerberos, authentication, common, settings, secure
import collections
import secrets
import aioconsole
import asyncio
import logging

ACCESS_KEY = "6f599f81"
NEX_VERSION = 30815
SETTINGS_PROFILE = "default"

HOST = "192.168.1.42"
BIND = "0.0.0.0"
AUTH_PORT = 1223
SECURE_PORT = 1224

SECURE_PASSWORD = "password"
SECURE_SERVER = "Quazal Rendez-Vous"

DEV_MODE = True
DEBUG = False

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("splatoon-nex")

User = collections.namedtuple("User", "pid name password")

USERS = [
    User(2, SECURE_SERVER, SECURE_PASSWORD),
    User(100, "guest", "MMQea3n!fsik"),
]
USERS_BY_NAME = {u.name: u for u in USERS}
USERS_BY_PID = {u.pid: u for u in USERS}


def derive_key(user):
    deriv = kerberos.KeyDerivationOld(65000, 1024)
    return deriv.derive_key(user.password.encode("ascii"), user.pid)


class AuthenticationServer(authentication.AuthenticationServer):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    async def login(self, client, username):
        log.info("login: %s", username)
        user = USERS_BY_NAME.get(username)
        if user is None:
            raise common.RMCError("RendezVous::InvalidUsername")
        return self.make_response(user)

    async def login_ex(self, client, username, extra_data):
        log.info("login_ex: %s", username)
        user = USERS_BY_NAME.get(username)
        if user is None and DEV_MODE:
            log.warning("Utilisateur inconnu '%s', repli sur guest", username)
            user = USERS_BY_NAME["guest"]
        if user is None:
            raise common.RMCError("RendezVous::InvalidUsername")
        return self.make_response(user)

    def make_response(self, user):
        server = USERS_BY_NAME[SECURE_SERVER]

        url = common.StationURL(
            scheme="prudps", address=HOST, port=SECURE_PORT,
            PID=server.pid, CID=1, type=2, sid=1, stream=10
        )

        conn_data = authentication.RVConnectionData()
        conn_data.main_station = url
        conn_data.special_protocols = []
        conn_data.special_station = common.StationURL()

        response = rmc.RMCResponse()
        response.result = common.Result.success()
        response.pid = user.pid
        response.ticket = self.generate_ticket(user, server)
        response.connection_data = conn_data
        response.server_name = "Splatoon server"
        return response

    def generate_ticket(self, source, target):
        s = self.settings
        user_key = derive_key(source)
        server_key = derive_key(target)
        session_key = secrets.token_bytes(s["kerberos.key_size"])

        internal = kerberos.ServerTicket()
        internal.timestamp = common.DateTime.now()
        internal.source = source.pid
        internal.session_key = session_key

        ticket = kerberos.ClientTicket()
        ticket.session_key = session_key
        ticket.target = target.pid
        ticket.internal = internal.encrypt(server_key, s)
        return ticket.encrypt(user_key, s)


class SecureConnectionServer(secure.SecureConnectionServer):
    def __init__(self):
        super().__init__()
        self.next_cid = 1

    async def register(self, client, urls):
        cid = self.next_cid
        self.next_cid += 1

        addr = client.remote_address()
        log.info("register: pid=%s cid=%s addr=%s", client.pid(), cid, addr)

        url = common.StationURL(
            scheme="prudp", address=addr[0], port=addr[1],
            PID=client.pid(), CID=cid, type=2, sid=1, stream=10
        )

        response = rmc.RMCResponse()
        response.result = common.Result.success()
        response.connection_id = cid
        response.public_station = url
        return response


async def main():
    s = settings.load(SETTINGS_PROFILE)
    s.configure(ACCESS_KEY, NEX_VERSION)

    auth_servers = [
        AuthenticationServer(s)
    ]
    secure_servers = [
        SecureConnectionServer(),
    ]

    server_key = derive_key(USERS_BY_NAME[SECURE_SERVER])

    log.info("Annonce de %s (auth:%d, secure:%d)", HOST, AUTH_PORT, SECURE_PORT)
    async with rmc.serve(s, auth_servers, BIND, AUTH_PORT):
        async with rmc.serve(s, secure_servers, BIND, SECURE_PORT, key=server_key):
            await aioconsole.ainput("Appuie sur Entrée pour quitter...\n")
    log.info("Serveur arrêté")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass