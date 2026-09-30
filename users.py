"""Comptes du serveur (en mémoire)."""
import collections

import config

User = collections.namedtuple("User", "pid name password")

USERS = [
    User(2, config.SECURE_SERVER_NAME, "password"),
    User(100, "guest", "MMQea3n!fsik"),
]

_BY_NAME = {u.name: u for u in USERS}
_BY_PID = {u.pid: u for u in USERS}


def get_by_name(name):
    return _BY_NAME.get(name)


def get_by_pid(pid):
    return _BY_PID.get(pid)


def secure_server_user():
    return _BY_NAME[config.SECURE_SERVER_NAME]
