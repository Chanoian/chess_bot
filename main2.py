import hashlib
import random
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from chess_engine import ChessEngine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Games.site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine_path = "/home/builder/chess_bot_gcloud/stockfish-11-linux/Linux/stockfish_20011801_x64"

db = SQLAlchemy(app)
PIECE_COLOR = ['white', 'black']
chess_engine = ChessEngine(engine_path=engine_path)


class Games(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    session_url = db.Column(db.String, unique=True, nullable=False)
    game_id = db.Column(db.String, unique=True, nullable=False)
    board = db.Column(db.PickleType(), unique=True, nullable=False)
    player_color = db.Column(db.String, unique=False, nullable=False)
    engine_level = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, session_url, game_id, board, player_color, engine_level):
        self.session_url = session_url
        self.game_id = game_id
        self.board = board
        self.player_color = player_color
        self.engine_level = engine_level


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
    if action == 'RevertMove':
        return revertMove(session)
    # if action == 'ResignGame':
    #     return resignGame(session)


def hash_session_url(session_url):
    hash = hashlib.sha1(session_url.encode("UTF-8")).hexdigest()
    game_id = hash[:10]
    return game_id


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
        game = db.session.query(Games).filter(Games.session_url == session_url).first()
        game_id = game.game_id
    except AttributeError:
        return False
    return game_id


def get_board_from_session_url(session_url):
    """
    """
    try:
        game = db.session.query(Games).filter(Games.session_url == session_url).first()
        board = game.board
    except AttributeError:
        return False
    return board


def get_engine_level_from_the_data_base(session_url):
    try:
        game = db.session.query(Games).filter(Games.session_url == session_url).first()
        engine_level = game.engine_level
    except AttributeError:
        return False
    return engine_level


def update_board_in_data_base(session_url, new_board):
    try:
        game = db.session.query(Games).filter(Games.session_url == session_url).first()
        game.board = new_board
        db.session.commit()
    except AttributeError:
        return False
    return True


def delete_row_in_database(session_url):
    try:
        game = db.session.query(Games).filter(Games.session_url == session_url).first()
    except AttributeError:
        return False
    db.session.delete(game)
    db.session.commit()
    return True


# def resignGame(session_url):
#     game_id = get_game_id_from_session_url(session_url=session_url)
#     if game_id:
#         berserberserk_client.board.resign_game(game_id=game_id)
#         delete_row_in_database(session_url=session_url)
#         reply_string = "Resigning the Game"
#     else: # when there is no game_id in database
#         reply_string = "You need to Start the game first"
#     reply = {"fulfillmentText": reply_string}
#     return jsonify(reply)

def move_generator(piece, board):
    if len(board) == 1:
        if piece == 'pawn' or piece == '':
            move = (board[0])
        else:
            move = (piece + board[0])
    elif len(board) == 2:
        if piece == 'pawn' or piece == '':
            move = board[0] + board[1]
        else:
            move = (piece + board[0] + board[1])
    else:
        print(piece, board)
    return move


def revertMove(session_url):
    board = get_board_from_session_url(session_url=session_url)
    print(board)
    if board:
        new_board = chess_engine.revert_two_moves(board=board)
    print(new_board)
    update_board_in_data_base(session_url=session_url, new_board=new_board)
    reply = {"fulfillmentText": "The Last two moves has been reverted"}
    return jsonify(reply)


def makeMove(parameters, session_url):
    board = parameters['Board']
    piece = parameters['ChessPiece']
    special_move = parameters['Specialmoves']
    if special_move == 'short_castle':
        move = 'O-O'
    elif special_move == 'long_castle':
        move = 'O-O-O'
    else:
        move = move_generator(piece=piece, board=board)
    print(move)
    board = get_board_from_session_url(session_url=session_url)
    print(board)
    if board:
        try:
            new_board = chess_engine.make_move(board, move=move)
        except ValueError as e:
            reply_string = "Your move " + move + " is not a valid Move "
            reply = {"fulfillmentText": reply_string}
            return jsonify(reply)
        engine_level = get_engine_level_from_the_data_base(session_url=session_url)
        engine_move, engine_board = chess_engine.let_the_engine_play(engine_level=engine_level, board=new_board)
        update_board_in_data_base(session_url=session_url, new_board=engine_board)
        reply_string = "You Played {0} ... My Move is {1}".format(move, engine_move)
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


def createChallengeAI(parameters, session_url):
    player_color = parameters['Color'] if parameters['Color'] else random.choice(PIECE_COLOR)
    engine_level = parameters['Level'] if parameters['Level'] else 5
    board = chess_engine.create_game()
    game_id = hash_session_url(session_url)
    game = Games(session_url, game_id, board, player_color, engine_level)
    session_url_query = Games.query.filter_by(session_url=session_url)
    if session_url_query.first():
        session_url_query.delete()
    db.session.add(game)
    db.session.commit()
    if player_color == 'black':
        engine_move, engine_board = chess_engine.let_the_engine_play(engine_level=engine_level, board=board)
        update_board_in_data_base(session_url=session_url, new_board=engine_board)
        reply_string = "Great!! The Game Started. and you are playing with {0} pieces and my first move is {1}".format(player_color, engine_move)
    else:    
        reply_string = "Great!! The Game Started. and you are playing with {0} pieces, It's your Move".format(player_color)
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
