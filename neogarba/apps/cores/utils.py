import uuid
from uuid_utils import uuid7 as _uuid7
from datetime import datetime


def generer_uuid7():
    return uuid.UUID(str(_uuid7()))


def generer_reference(prefixe):
    date_str = datetime.now().strftime('%Y%m%d')
    uuid_hex = str(_uuid7()).replace('-', '')
    uuid_part = uuid_hex[-10:].upper()
    return f"{prefixe}-{date_str}-{uuid_part}"

PREFIXES = {
    'utilisateur': 'USR',
    'adresse': 'ADR',
    'categorie': 'CAT',
    'plat': 'PLT',
    'option': 'OPT',
    'panier': 'PAN',
    'ligne_panier': 'LPN',
    'commande': 'CMD',
    'ligne_commande': 'LCD',
    'paiement': 'PAY',
    'livraison': 'LIV',
    'codeotp':'OTP'
}










