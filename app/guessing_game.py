import os
import redis

from flask import Flask
from flask import render_template
from pymongo import MongoClient

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient(
    'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ[
        'MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379),
                          db=os.environ.get("REDIS_DB", 0))


@application.route('/')
def index():
    doc = db.guessing_game.find_one()
    if doc is None:
        db.guessing_game.insert_one(
            {
                "guess": ['_', '_', '_', '_'], "show": ['_', '_', '_', '_'], "secret": ['', '', '', ''], "index": 0,
                "index2": 0, "attempt": 0
            }
        )
    return render_template("index.html")


@application.route('/get_start')
def get_ready():
    doc = db.guessing_game.find_one()
    if doc is None:
        db.guessing_game.insert_one(
            {
                "guess": ['_', '_', '_', '_'], "show": ['_', '_', '_', '_'], "secret": ['', '', '', ''], "index": 0,
                "index2": 0, "attempt": 0
            }
        )

    body = "<h1>Step 1 - Get Start</h1>"
    body += "<h3>Instruction: Pick your 4 secret characters and do not let anyone see it!</h3>"

    """ show the secret word"""

    body += "    "
    body += doc["show"][0]
    body += "    "
    body += doc["show"][1]
    body += "    "
    body += doc["show"][2]
    body += "    "
    body += doc["show"][3]

    body += '<h3><a href="/setA" class="button">Letter: A</a></h3>'
    body += '<h3><a href="/setB" class="button">Letter: B</a></h3>'
    body += '<h3><a href="/setC" class="button">Letter: C</a></h3>'
    body += '<h3><a href="/setD" class="button">Letter: D</a></h3>'

    body += '<button><a href="/">Back</a></button>'

    if doc["index"] > 0:
        body += '<button><a href="/reset">Reset</a></button>'
    if doc["index"] >= 4:
        body += '<button><a href="/game_started">Game Start</a></button>'

    return body


def updateSecret(x, y):
    doc = db.guessing_game

    if y["index"] > 3:
        doc.update_one({}, {"$set": {"index": 0}})

    if y["index"] == 0:
        doc.update_one({}, {"$set": {"show.0": "*"}})
        doc.update_one({}, {"$set": {"secret.0": x}})

    elif y["index"] == 1:
        doc.update_one({}, {"$set": {"show.1": "*"}})
        doc.update_one({}, {"$set": {"secret.1": x}})

    elif y["index"] == 2:
        doc.update_one({}, {"$set": {"show.2": "*"}})
        doc.update_one({}, {"$set": {"secret.2": x}})

    elif y["index"] == 3:
        doc.update_one({}, {"$set": {"show.3": "*"}})
        doc.update_one({}, {"$set": {"secret.3": x}})

    doc.update_one({}, {"$set": {"index": y["index"] + 1}})


@application.route('/game_started')
def game_started():
    doc = db.guessing_game.find_one()
    body = "<h1>Step 2 - Let's Begin</h1>"
    body += "<h3>Instruction: Try to guess your friend's secret :)</h3>"

    body += "    "
    body += doc["guess"][0]
    body += "    "
    body += doc["guess"][1]
    body += "    "
    body += doc["guess"][2]
    body += "    "
    body += doc["guess"][3]
    body += "<h1></h1>"

    body += f'attempt: {doc["attempt"]}'

    body += '<h3><a href="/guessA" class="button">Letter: A</a></h3>'
    body += '<h3><a href="/guessB" class="button">Letter: B</a></h3>'
    body += '<h3><a href="/guessC" class="button">Letter: C</a></h3>'
    body += '<h3><a href="/guessD" class="button">Letter: D</a></h3>'

    if doc["guess"][3] != "_":
        attempt = doc["attempt"]
        return render_template("win.html", attempt=attempt)
    return body


@application.route('/setA')
def setA():
    doc = db.guessing_game.find_one()
    updateSecret("A", doc)
    return get_ready()


@application.route('/setB')
def setB():
    doc = db.guessing_game.find_one()
    updateSecret("B", doc)
    return get_ready()


@application.route('/setC')
def setC():
    doc = db.guessing_game.find_one()
    updateSecret("C", doc)
    return get_ready()


@application.route('/setD')
def setD():
    doc = db.guessing_game.find_one()
    updateSecret("D", doc)
    return get_ready()


def guessSecret(x, y):
    if y["guess"][3] != "_":
        return

    doc = db.guessing_game

    if y["index2"] > 3:
        doc.update_one({}, {"$set": {"index2": 0}})

    if y["index2"] == 0:
        if x == y["secret"][0]:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            doc.update_one({}, {"$set": {"index2": y["index2"] + 1}})
            doc.update_one({}, {"$set": {"guess.0": x}})
            return
        else:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            return

    elif y["index2"] == 1:
        if x == y["secret"][1]:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            doc.update_one({}, {"$set": {"index2": y["index2"] + 1}})
            doc.update_one({}, {"$set": {"guess.1": x}})
            return
        else:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            return

    elif y["index2"] == 2:
        if x == y["secret"][2]:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            doc.update_one({}, {"$set": {"index2": y["index2"] + 1}})
            doc.update_one({}, {"$set": {"guess.2": x}})
            return
        else:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            return

    elif y["index2"] == 3:
        if x == y["secret"][3]:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            doc.update_one({}, {"$set": {"index2": y["index2"] + 1}})
            doc.update_one({}, {"$set": {"guess.3": x}})
            return
        else:
            doc.update_one({}, {"$set": {"attempt": y["attempt"] + 1}})
            return


@application.route('/guessA')
def guessA():
    doc = db.guessing_game.find_one()
    guessSecret("A", doc)
    return game_started()


@application.route('/guessB')
def guessB():
    doc = db.guessing_game.find_one()
    guessSecret("B", doc)
    return game_started()


@application.route('/guessC')
def guessC():
    doc = db.guessing_game.find_one()
    guessSecret("C", doc)
    return game_started()


@application.route('/guessD')
def guessD():
    doc = db.guessing_game.find_one()
    guessSecret("D", doc)
    return game_started()


@application.route('/reset')
def reset():
    doc = db.guessing_game

    doc.update_one({}, {"$set": {"guess.0": "_"}})
    doc.update_one({}, {"$set": {"guess.1": "_"}})
    doc.update_one({}, {"$set": {"guess.2": "_"}})
    doc.update_one({}, {"$set": {"guess.3": "_"}})

    doc.update_one({}, {"$set": {"show.0": "_"}})
    doc.update_one({}, {"$set": {"show.1": "_"}})
    doc.update_one({}, {"$set": {"show.2": "_"}})
    doc.update_one({}, {"$set": {"show.3": "_"}})

    doc.update_one({}, {"$set": {"secret.0": ""}})
    doc.update_one({}, {"$set": {"secret.1": ""}})
    doc.update_one({}, {"$set": {"secret.2": ""}})
    doc.update_one({}, {"$set": {"secret.3": ""}})

    doc.update_one({}, {"$set": {"index": 0}})
    doc.update_one({}, {"$set": {"index2": 0}})
    doc.update_one({}, {"$set": {"attempt": 0}})

    return get_ready()


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
