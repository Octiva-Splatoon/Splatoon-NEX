"""Configuration du serveur. Modifie uniquement ce fichier pour changer les réglages."""

# --- NEX ---------------------------------------------------------------
ACCESS_KEY = "6f599f81"       # clé d'accès du jeu (à vérifier pour Splatoon)
NEX_VERSION = 30815           # version NEX (à vérifier pour Splatoon)
SETTINGS_PROFILE = "default"  # profil de réglages de NintendoClients

# --- Réseau ------------------------------------------------------------
HOST = "127.0.0.1"   # IP annoncée au client (mets ton IPv4 LAN pour la Wii U)
BIND = "0.0.0.0"     # adresse d'écoute
AUTH_PORT = 1223
SECURE_PORT = 1224

# --- Serveur -----------------------------------------------------------
SERVER_NAME = "Splatoon server"
SECURE_SERVER_NAME = "Quazal Rendez-Vous"

# --- Développement -----------------------------------------------------
DEV_MODE = True   # True : un utilisateur inconnu est associé à "guest"
DEBUG = False     # True : logs détaillés
