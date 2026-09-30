"""Dérivation de clés et génération des tickets Kerberos."""
import secrets

from nintendo.nex import common, kerberos


def derive_key(user):
    deriv = kerberos.KeyDerivationOld(65000, 1024)
    return deriv.derive_key(user.password.encode("ascii"), user.pid)


def generate_ticket(nex_settings, source, target):
    """Crée le ticket chiffré qu'un client utilisera pour le serveur sécurisé."""
    user_key = derive_key(source)
    server_key = derive_key(target)
    session_key = secrets.token_bytes(nex_settings["kerberos.key_size"])

    internal = kerberos.ServerTicket()
    internal.timestamp = common.DateTime.now()
    internal.source = source.pid
    internal.session_key = session_key

    ticket = kerberos.ClientTicket()
    ticket.session_key = session_key
    ticket.target = target.pid
    ticket.internal = internal.encrypt(server_key, nex_settings)
    return ticket.encrypt(user_key, nex_settings)
