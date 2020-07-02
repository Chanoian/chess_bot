import berserk
from berserk import exceptions
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, make_response, jsonify


with open('lichess.token') as f:
    token = f.read()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Games.site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

berserk_session = berserk.TokenSession(token)
berserk_client = berserk.Client(berserk_session)

class Games(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    session_url = db.Column(db.String, unique=True, nullable=False)
    game_id = db.Column(db.String, unique=True, nullable=False)
    
    def __init__(self, session_url, game_id):
        self.session_url = session_url
        self.game_id = game_id

db.create_all()

@app.route('/')
def helloWorld():
    return 'Hello, World'



@app.route('/api/v1/assistant', methods=['POST'])
def mainAssistant():
    dialogflow_data = request.get_json(silent=True)
    action, parameters, session = processDialogFlowData(dialogflow_data)
    if action == 'CreateGame':
        return createChallengeAI(parameters, session)
    if action == 'MakeMove':
        return makeMove(parameters, session)
    if action == 'ResignGame':
        return resignGame(session)



def processDialogFlowData(json_payload):
    """
    This Function Will get the json Data from Dialogflow and return the action and any parameter
    """
    action = json_payload["queryResult"]["action"]
    parameters = json_payload["queryResult"]["parameters"]
    session_url = json_payload["session"]                                                                                                                                                                                                             
    return action, parameters, session_url

def get_game_id_from_session_url(session_url):
    try:
        game = db.session.query(Games).filter(Games.session_url==session_url).first()
        game_id = game.game_id
    except AttributeError:
        return False
    return game_id

def delete_row_in_database(session_url):
    try:
        game = db.session.query(Games).filter(Games.session_url==session_url).first()
    except AttributeError:
        return False
    db.session.delete(game)
    db.session.commit()
    return True

def resignGame(session_url):
    game_id = get_game_id_from_session_url(session_url=session_url)
    if game_id:
        berserk_client.board.resign_game(game_id=game_id)
        delete_row_in_database(session_url=session_url)
        reply_string = "Resigning the Game"
    else: # when there is no game_id in database
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


def makeMove(parameters, session_url):
    game_id = get_game_id_from_session_url(session_url=session_url)
    if game_id:
        try:
            berserk_client.board.make_move(game_id=game_id, move='e2e4')
        except exceptions.ResponseError as e:
            reply_string = "This is not a valid Move " + e.cause['error']
        reply_string = "Nice Move"
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)

def createChallengeAI(parameters, session_url):
    level = parameters['Level'] if parameters['Level'] else 5
    color = parameters['Color'] if parameters['Color'] else 'random'
    response = berserk_client.challenges.create_ai(level=level, color=color)
    game_id = response['id']
    game = Games(session_url, game_id)
    session_url_query = Games.query.filter_by(session_url=session_url)
    if session_url_query.first():
        session_url_query.delete()
    db.session.add(game)
    db.session.commit()
    game_export_response = berserk_client.games.export(game_id=game_id)
    player_color = 'black' if 'aiLevel' in game_export_response['players']['white'] else 'white'
    reply_string = "Great, The Game Started and you are playing with {0} pieces".format(player_color)
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)