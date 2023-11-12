import os
import json
import time
import logging
import logging.handlers

from datetime import datetime
from flask import (
        Flask,
        request,
        Response,
        render_template,
        render_template_string,
        )

import player

app = Flask(__name__)

""" #LOGGING """

SERVER_LOG_LEVEL   = 60
SERVER_ERROR_LEVEL = 70

MAX_LOG_FILE_SIZE  = 1024*5

handler_file_log = logging.handlers.RotatingFileHandler("server.log", maxBytes=MAX_LOG_FILE_SIZE)
handler_file_log.setLevel(SERVER_LOG_LEVEL)
handler_file_log.setFormatter(logging.Formatter("[%(asctime)s] %(module)s: %(message)s", "%d/%m/%Y %H:%M:%S"))

app.logger.addHandler(handler_file_log)

def log(msg, *args, **kwargs):
    return app.logger.log(SERVER_LOG_LEVEL, msg, *args, **kwargs)

def log_error(msg, *args, **kwargs):
    return app.logger.log(SERVER_ERROR_LEVEL, "ERROR: " + msg, *args, **kwargs)

""" #PLAYERS """

GAME_MASTER = "iamthecreatorofthisworld"

player.register("cruel")
player.register("astral")
player.register("violao")
player.register("jogador")
player.register("teclado")
player.register("mestre")

""" #GAME-CONSTANTS """

ATTRIBUTES_POINTS = 5
ATTRIBUTES = ([
    "Força",
    "Reflexos",
    "Precição",
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

REGISTRATION_ERRORS = ([
    "Registrado",
    "Caixa nome invalida",
    "Caixa sexo invalida",
    "Caixa nascimento invalida",
    "Caixa descrição visual invalida",
    "Caixa história invalida",
    "Abuso de pontos"
    ])

documents_dir = "documents/"
documents = os.listdir(documents_dir)
doc_index = 0

__uid__ = 0

def generate_uid():
    global __uid__
    __uid__ += 1
    return "c" + str(__uid__)

__msg__ = []

def add_message(msg, user):
    global __msg__
    msg_time = datetime.now().strftime("%H:%M:%S")
    __msg__.append([msg, msg_time, user])

def pop_message():
    global __msg__
    if len(__msg__) > 0:
        return __msg__.pop()
    return ["", "", ""]

def build_component_params():
    params = request.form if request.method == "POST" else {}
    return { "uid": generate_uid(), **params }

def readfile(filepath):
    content = ""
    with open(filepath, "r") as file:
        content = file.read()
    return content

def serve_file(filepath, modifier=None, modifier_params={}):
    content = ""
    mimetype = "text/plain"

    with open(filepath, "rb") as file:
        content = file.read().decode("utf-8")

    if modifier and callable(modifier):
        # TODO: having `**` is making it specific.
        content = modifier(content, **modifier_params)

    if filepath.endswith(".css"):
        mimetype = "text/css"
    elif filepath.endswith(".html"):
        mimetype = "text/html"
    elif filepath.endswith(".js"):
        mimetype = "application/javascript"
    elif filepath.endswith(".mp3"):
        mimetype = "audio/mpeg"

    if content == "":
        content = "<p>404 ERROR</p>"

    return Response(content, mimetype=mimetype)

@app.route("/")
def __index__():
    return render_template("index.html")

@app.route("/component/<name>", methods=["GET", "POST"])
def __component__(name):
    params = build_component_params()
    return serve_file(f"components/{name}.html", render_template_string, params)

@app.route("/component/list/<name>", methods=["POST"])
def __component_list__(name):
    component = readfile(f"components/{name}.html")
    if component == "":
        return "", 400

    path = request.form["path"]
    if not os.path.isdir(path):
        return "", 400

    output = ""

    for file in os.listdir(path):
        params = build_component_params()
        file_name = ".".join(file.split(".")[:-1])

        output += render_template_string(component,
                                         file_name=file_name,
                                         full_path=path + "/" + file,
                                         **params)

    return output, 200

@app.route("/document")
def __document__():
    global doc_index
    doc_index = 0

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/document/previous")
def __document_previous__():
    global doc_index
    doc_index -= 1

    if doc_index < 0:
        doc_index = len(documents) - 1

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/document/next")
def __document_name__():
    global doc_index
    doc_index += 1

    if doc_index >= len(documents):
        doc_index = 0

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/messages/<user>", methods=["GET", "POST"])
def __messages__(user):

    add_message("Hey!", "M")

    if user == GAME_MASTER and request.method == "GET":
        content = ""
        while True:
            msg, msg_time, user = pop_message()
            if msg == "":
                break
            msg = f"<p>[{msg_time}][{user}]: {msg}</p>"
            content += msg
        return content, 200
    elif request.method == "POST":
        message = request.form["message"]
        add_message("<p>" + message + "</p>")
        return "", 200
    return "", 400

@app.route("/player-info/<name>")
def __player_info__(name):
    player_info = players.get(name)
    if player_info == None:
        return "", 400

    return render_template("player-info.html", name=name, **player_info)

@app.route("/players")
def __player__():
    s = ""
    for name, player in players.items():
        s += f'<div class="char-entry" hx-get="/player-info/{name}" hx-trigger="click" hx-swap="none">{name}</div>'
    return Response(s)

@app.route("/player/<player_id>")
def __player_page__(player_id):
    return serve_file("pages/player.html")

@app.route("/player-list")
def __player_list__():
    html = ""

    for filepath in os.listdir("documents/players"):
        name, ext = filepath.split(".")
        html += "<div "
        html += f'hx-get="/player-doc/{name}"'
        html += 'hx-target=".char-info"'
        html += ">"
        html += f"{name}"
        html += "</div>\n"
    return html

@app.route("/player-register", methods=["POST"])
def __player_register__():
    key = request.form.get("key", "[unknown]")

    try:
        player.edit(**request.form)
    except player.ClientError as e:
        return str(e), 200
    except player.ServerError as e:
        log_error(str(e))
        return "Erro desconhecido", 200

    log(f"{key} updated informations")

    return "Salvo", 200

@app.post("/validate")
def __validate__():
    id_ = request.form["id"]

    if id_ == GAME_MASTER:
        return render_template("master.html")
    try:
        log(f"{id_} accessed the registration page")
        p = player.get(id_)
        return render_template(
                "player-register.html", **p,
                knowledges_points_n=player.KNOWLEDGES_POINTS,
                attributes_points_n=player.ATTRIBUTES_POINTS)
    except player.ClientError as e:
        return str(e), 200, {"HX-Retarget": "#error"}
    except player.ServerError as e:
        log_error(e)
        return "Erro desconhecido", 200, {"HX-Retarget": "#error"}
