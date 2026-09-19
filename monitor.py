import json
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


ARQUIVO = Path("data/monitoramentos.json")


def formatDate(data):

    dt = datetime.strptime(data, "%d/%m/%Y")

    dt = dt.replace(
        tzinfo=ZoneInfo("America/Sao_Paulo")
    )

    return int(dt.timestamp() * 1000)


def loadTrackings():
    if not ARQUIVO.exists():
        return []

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def saveTrackings(monitoramentos):
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)

    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(
            monitoramentos,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def createTracking(
    origem,
    destino,
    data,
    user_id
):
    monitoramentos = loadTrackings()

    monitor = findTracking(
        monitoramentos,
        origem,
        destino,
        data,
    )

    # Já existe
    if monitor:

        if user_id not in monitor["users"]:
            monitor["users"].append(user_id)

            saveTrackings(monitoramentos)

        return monitor

    # Criar novo
    monitor = {
        "id": str(uuid4()),
        "origem": origem,
        "destino": destino,
        "data": data,
        "detalhe": 33,
        "quantidade": 1,
        "users": [user_id],
    }

    monitoramentos.append(monitor)

    saveTrackings(monitoramentos)

    return monitor


def findTracking(
    monitoramentos,
    origem,
    destino,
    data,
):

    for monitor in monitoramentos:

        if (
            monitor["origem"] == origem
            and monitor["destino"] == destino
            and monitor["data"] == data
        ):
            return monitor

    return None


def removeUser(monitor_id, user_id):
    monitoramentos = loadTrackings()

    for monitor in monitoramentos:

        if monitor["id"] == monitor_id:

            if user_id not in monitor["users"]:
                return False

            monitor["users"].remove(user_id)

            # Ninguém mais está interessado
            if not monitor["users"]:
                monitoramentos.remove(monitor)

            saveTrackings(monitoramentos)

            return True

    return False


def getTrackingsByUser(user_id) :
    monitoramentos  = loadTrackings()

    r = []

    for monitor in monitoramentos :
        if user_id in monitor["users"] :
            r.append(monitor)

    return r


def deleteTracking(monitor_id):
    monitoramentos = loadTrackings()

    temp = [
        monitor
        for monitor in monitoramentos
        if monitor["id"] != monitor_id
    ]

    if len(temp) == len(monitoramentos):
        return False

    saveTrackings(temp)

    return True
