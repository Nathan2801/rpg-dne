import os
import json

"""
API

exists(key: string) - Check if a player exists.

get(key: string) - Get player attributes.

register(key: string) - Register a new player to be created.

unregister(key: string) - Unregister a player.

edit(key: string, **kwargs) - Edit a existing player.

"""

""" #CONTANTS """

ATTRIBUTES_POINTS = 5
ATTRIBUTES = ([
    "Força",
    "Reflexos",
    "Precisão",
    "Presença",
    "Agilidade",
    "Inteligência",
    "Furtividade"
    ])

KNOWLEDGES_POINTS = 5
KNOWLEDGES = ([
    "Medicina",
    "Tecnologia",
    "Balística",
    "Combate",
    "Investigação",
    "Furto",
    "Línguas"
    ])

""" #ERRORS """

class ServerError(Exception):
    pass

class ClientError(Exception):
    pass

ERR_MISSING_KEY = "Chave vazia"
ERR_MISSING_SEX = "Caixa (sexo) vazia"
ERR_MISSING_JOB = "Caixa (ocupacao) vazia"
ERR_MISSING_NAME = "Caixa (nome) vazia"
ERR_MISSING_BIRTH = "Caixa (nascimento) vazia"
ERR_MISSING_VISUAL = "Caixa (caracteristicas) vazia"
ERR_MISSING_HISTORY = "Caixa (historia) vazia"
ERR_MISSING_ATTRIBUTES = "Atributos nao listados"
ERR_MISSING_KNOWLEDGES = "Conhecimentos nao listados"
ERR_ABUSE_OF_POINTS = "Abuso de pontos"

ERR_INVALID_KEY = "Chave invalida"
ERR_INVALID_JSON_FILE = "Format do aquivo do jogador invalido"
ERR_USER_ALREADY_REGISTERED = "Usuario ja registrado"
ERR_USER_NOT_REGISTERED = "Usuario nao registrado"

""" #API """

__DIRECTORY__   = "players/"
__FILE_FORMAT__ = "{}.html"


def _path(key):
    file = __FILE_FORMAT__.format(key)
    path = __DIRECTORY__ + file
    return path


def _empty_player(key):
    return ({
        "key": key,
        "sex": "",
        "job": "",
        "name": "",
        "birth": "",
        "visual": "",
        "history": "",
        "attributes": {attr: 0 for attr in ATTRIBUTES},
        "knowledges": {know: 0 for know in KNOWLEDGES}
        })


def _validate(d):
    x = d.get("sex")
    if x == None or x == "": raise ClientError(ERR_MISSING_SEX)
    x = d.get("job")
    if x == None or x == "": raise ClientError(ERR_MISSING_JOB)
    x = d.get("key")
    if x == None or x == "": raise ClientError(ERR_MISSING_KEY)
    x = d.get("name")
    if x == None or x == "": raise ClientError(ERR_MISSING_NAME)
    x = d.get("birth")
    if x == None or x == "": raise ClientError(ERR_MISSING_BIRTH)
    x = d.get("visual")
    if x == None or x == "": raise ClientError(ERR_MISSING_VISUAL)
    x = d.get("history")
    if x == None or x == "": raise ClientError(ERR_MISSING_HISTORY)

    i = 0
    v = 0
    for k in d:
        if k in ATTRIBUTES:
            i += 1
            v += int(d[k])
    if i != len(ATTRIBUTES):
        raise ServerError(ERR_MISSING_ATTRIBUTES)
    if v > ATTRIBUTES_POINTS:
        raise ClientError(ERR_ABUSE_OF_POINTS)

    i = 0
    v = 0
    for k in d:
        if k in KNOWLEDGES:
            i += 1
            v += int(d[k])
    if i != len(KNOWLEDGES):
        raise ServerError(ERR_MISSING_KNOWLEDGES)
    if v > KNOWLEDGES_POINTS:
        raise ClientError(ERR_ABUSE_OF_POINTS)

    return None


def exists(key):
    return os.path.exists(_path(key))


def get(key):
    if not exists(key):
        raise ClientError(ERR_INVALID_KEY)

    d = {}
    with open(_path(key), "r") as f:
        s = f.read()
        try: d = json.loads(s)
        except: raise ServerError(ERR_INVALID_JSON_FILE)

    return d


def register(key):
    if not os.path.exists("players/"):
        os.mkdir("players")
    if not exists(key):
        with open(_path(key), "w+") as f:
            f.write(json.dumps(_empty_player(key), indent=2))
    # TODO: check if our file contains the correct format.
    return None


def unregister(key):
    os.remove(_path(key))
    return None


def edit(**kwargs):
    _validate(kwargs)

    key = kwargs["key"]
    if not exists(key):
        raise ClientError(ERR_USER_NOT_REGISTERED)

    d = {"attributes": {}, "knowledges": {}}
    for k in kwargs:
        if k in ATTRIBUTES:
            d["attributes"][k] = kwargs[k]
        elif k in KNOWLEDGES:
            d["knowledges"][k] = kwargs[k]
        else:
            d[k] = kwargs[k]

    with open(_path(key), "w") as f:
        f.write(json.dumps(d))
    return None
