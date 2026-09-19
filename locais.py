import json
from pathlib import Path

ARQUIVO = Path("data/locais.json")


def loadLocations():
    if not ARQUIVO.exists():
        return []

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def getLocationById(location_id):
    for local in loadLocations():
        if local["id"] == location_id:
            return local

    return None