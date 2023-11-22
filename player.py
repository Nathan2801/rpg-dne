import os
import json

""" #CONTANTS """

ATTRIBUTES_POINTS = 6
ATTRIBUTES = ([
    "Força",
    "Reflexos",
    "Precisão",
    "Presença",
    "Percepção",
    "Agilidade",
    "Inteligência",
    "Furtividade"
    ])

KNOWLEDGES_POINTS = 6
KNOWLEDGES = ([
    "Medicina",
    "Tecnologia",
    "Balística",
    "Combate",
    "Investigação",
    "Comunicação",
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
ERR_INVALID_JSON_FILE = "Formato do aquivo do jogador invalido"
ERR_USER_ALREADY_REGISTERED = "Usuario ja registrado"
ERR_USER_NOT_REGISTERED = "Usuario nao registrado"

""" API constants
"""
__DIRECTORY__   = "players/"
__FILE_FORMAT__ = "{}.json"

""" Hidden functions
"""
def _path(key):
    """Return the path of the file associated with {key}.
    """
    file = __FILE_FORMAT__.format(key)
    path = __DIRECTORY__ + file
    return path


def _empty_sheet(key):
    """Return the structure of a player sheet.
    """
    return ({
        "key": key,
        "sex": "",
        "job": "",
        "name": "",
        "birth": "",
        "visual": "",
        "history": "",
        "attributes": {attr: 0 for attr in ATTRIBUTES},
        "knowledges": {know: 0 for know in KNOWLEDGES},
        "inventory": {},
        "live": {
            "pe": 2,
            "pv": 10
            }
        })


def _write(key, data):
    """Write the dictionary {data} to a file associated with {key}.
    """
    with open(_path(key), "w") as file:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        file.write(content)
    return None


def _validate(d):
    """ Validate 'attributes' and 'knowledges'.

    NOTE: just works for html forms where all
    information is tied together (there is no
    more levels of dictionaries).
    """
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


def _exists(key):
    """Check if a player has already been registered.
    """
    return os.path.exists(_path(key))


def _register(key):
    """Create a json file containing the player structure.
    """
    _write(key, _empty_sheet(key))
    return None


def _fill_structure(a, b, strict=True):
    """Fill a dictionary structure with another dictionary.

    This tries to fill dictionary {a} with the values of
    dictionary {b}.

    The {strict} boolean argument defines what we do when
    we find a key that exists on {b} but not on {a}. If the
    value is True it will just ignore, otherwise it will
    create the key on the dictionary {a}.

    Example:
    >>> a = {"name": "", "age": 0}
    >>> b = {"age": 18}
    >>> print(_fill_structure(a, b)) # {"name": "", "age": 18}
    """
    for key in b.keys():
        if key in a:
            value = b[key]
            if type(a[key]) == type({}) and type(b[key]) == type({}):
                value = _fill_structure(a[key], b[key], strict=strict)
            a[key] = value
        elif not strict:
            a[key] = b[key]
    return a


def _guarantee_structure(key):
    """Rewrite the json file to guarantee it contains the
    correct structure.
    """
    player = get(key)
    base = _empty_sheet(key)

    _write(key, _fill_structure(base, player))
    return None


""" API functions
"""
def get(key):
    """Get a player information.
    """
    if not _exists(key):
        raise ClientError(ERR_INVALID_KEY)

    parsed = None
    result = _empty_sheet(key)

    with open(_path(key), "r") as f:
        s = f.read()
        try: parsed = json.loads(s)
        except: raise ServerError(ERR_INVALID_JSON_FILE)

    for k in parsed:
        if k == "attributes":
            for k_, v_ in parsed[k].items():
                result[k][k_] = v_
        elif k == "knowledges":
            for k_, v_ in parsed[k].items():
                result[k][k_] = v_
        else:
            result[k] = parsed[k]

    return result


def register(key):
    """Register a new player with certain {key}.
    """
    if not os.path.exists("players/"):
        os.mkdir("players")

    if _exists(key):
        _guarantee_structure(key)
    else:
        _register(key)

    return None


def unregister(key):
    """Delete the player associate with {key}.
    """
    os.remove(_path(key))
    return None


def edit(key, is_form=False, strict_fill=True):
    """Edit player information.

    Edit accept two variables the player {key} and a
    boolean value that inform if you are passing a
    single level dictionary (is_form=True) or a
    structure dictionary (is_form=False).

    The formats discussed before are:

    * single level dictionary - where all information is
    contained in a single level of dictionary, there are
    no keys that contains dictionary, only keys and values.

    * structured dictionary - where the format of the
    dictionary follow the same structure as the normal
    player structure.

    Usage:
    >>> edit = player.edit(key, is_form=True)
    >>> edit(content)
    """
    def inner(content):
        sheet = get(key)

        if is_form:
            for k in content.keys():
                if k in ATTRIBUTES:
                    sheet["attributes"][k] = content[k]
                elif k in KNOWLEDGES:
                    sheet["knowledges"][k] = content[k]

        _write(key, _fill_structure(sheet, content, strict=strict_fill))

        return None
    return inner


def set_inventory_slot(key, slot, item):
    """Change the player inventory
    """
    edit_ = edit(key, is_form=False, strict_fill=False)
    edit_({"inventory": {slot: item}})

    return None

