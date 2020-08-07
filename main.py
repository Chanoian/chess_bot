import random
import os
from sqlalchemy import engine, create_engine, Column, Integer, PickleType, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from chess_engine import ChessEngine

Base = declarative_base()
app = Flask(__name__)
db_user = 'root_sql_db'
db_password = 'chesstoremember'
db_name = 'chess_games'
cloud_sql_connection_name = 'chess-bot-cloud-run:us-central1:sql-instance'
db_socket_dir = '/cloudsql'
stockfish_engine_path = "./stockfish_20011801_x64"
sql_pass = 'oO4EPbGwF5tiCH0e'
db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
}
PIECE_COLOR = ['white', 'black']
chess_engine = ChessEngine(engine_path=stockfish_engine_path)


class Games(Base):
    __tablename__ = "game"
    _id = Column("id", Integer, primary_key=True)
    session_url = Column(VARCHAR(200), unique=True, nullable=False)
    board = Column(PickleType(), nullable=False)
    player_color = Column(VARCHAR(20), unique=False, nullable=False)
    engine_level = Column(Integer, unique=False, nullable=False)


db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
pool = create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
    engine.url.URL(
        drivername="mysql+pymysql",
        username=db_user,  # e.g. "my-database-user"
        password=db_password,  # e.g. "my-database-password"
        database=db_name,  # e.g. "my-database-name"
        query={
            "unix_socket": "{}/{}".format(
                db_socket_dir,  # e.g. "/cloudsql"
                cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
        }
    ),
    **db_config
)

Base.metadata.create_all(bind=pool)
Session = sessionmaker(bind=pool)


@app.route('/')
def helloWorld():
    return 'It Works !!'


@app.route('/api/v1/assistant', methods=['POST'])
def mainAssistant():
    dialogflow_data = request.get_json(silent=True)
    action, parameters, session = processDialogFlowData(dialogflow_data)
    if action == 'CreateGame':
        return CreateGame(parameters, session)
    if action == 'MakeMove':
        return makeMove(parameters, session)
    if action == 'RevertMove':
        return revertMove(session)
    if action == 'ResignGame':
        return resignGame(session)
    if action == 'ShowValidMoves':
        return showValidMoves(session)


def processDialogFlowData(json_payload):
    """
    This Function Will get the json Data from Dialogflow and return the action and any parameter
    """
    action = json_payload["queryResult"]["action"]
    parameters = json_payload["queryResult"]["parameters"]
    session_url = json_payload["session"]                                                                                                                                                                       
    return action, parameters, session_url


def get_board_from_session_url(session_url):
    """
    """
    try:
        session = Session()
        game = session.query(Games).filter(Games.session_url == session_url).first()
        board = game.board
        session.close()
    except AttributeError:
        return False
    return board


def get_engine_level_from_the_data_base(session_url):
    try:
        session = Session()
        game = session.query(Games).filter(Games.session_url == session_url).first()
        engine_level = game.engine_level
        session.close()
    except AttributeError:
        return False
    return engine_level


def update_board_in_data_base(session_url, new_board):
    try:
        session = Session()
        game = session.query(Games).filter(Games.session_url == session_url).first()
        game.board = new_board
        session.commit()
    except AttributeError:
        return False
    return True


def delete_row_in_database(session_url):
    try:
        session = Session()
        game = session.query(Games).filter(Games.session_url == session_url).first()
        session.delete(game)
        session.commit()
        session.close()
    except:
        return False
    return True


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
        return False
    return move


def showValidMoves(session_url):
    board = get_board_from_session_url(session_url=session_url)
    if board:
        reply_string = chess_engine.return_valid_moves(board)
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": str(reply_string)}
    return jsonify(reply)


def revertMove(session_url):
    board = get_board_from_session_url(session_url=session_url)
    if board:
        try:
            new_board = chess_engine.revert_two_moves(board=board)
            update_board_in_data_base(session_url=session_url, new_board=new_board)
            reply_string = "The Last two moves have been reverted, It's your move"
        except IndexError:
            reply_string = "There is nothing to be reverted"  
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


def resignGame(session_url):
    if delete_row_in_database(session_url=session_url):
        reply_string = "Your game has been ended !"
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
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
        if not move:
            reply_string = "I didn't understand your move, Please say it again!"
            reply = {"fulfillmentText": reply_string}
            return jsonify(reply)
    board = get_board_from_session_url(session_url=session_url)
    if board:
        try:
            new_board = chess_engine.make_move(board, move=move)
        except ValueError:
            reply_string = "Your move " + move + " is not a valid Move, Please try again "
            reply = {"fulfillmentText": reply_string}
            return jsonify(reply)
        board_status = chess_engine.validate_board_status(new_board)
        if board_status == 'Checkmate':
            reply_string = "You Played " + str(move) + ' ' + str(board_status)
            reply = {"fulfillmentText": reply_string}
            return jsonify(reply)
        engine_level = get_engine_level_from_the_data_base(session_url=session_url)
        engine_move, engine_board = chess_engine.let_the_engine_play(engine_level=engine_level, board=new_board)
        engine_board_status = chess_engine.validate_board_status(engine_board)
        if engine_board_status == 'Checkmate':
            reply_string = "My Move is " + str(engine_board) + ' ' + str(engine_board_status)
            reply = {"fulfillmentText": reply_string}
            return jsonify(reply)
        update_board_in_data_base(session_url=session_url, new_board=engine_board)
        reply_string = "You Played " + str(move) + ' ' + str(board_status) + "... My Move is " + str(engine_move) + ' ' + str(engine_board_status)
    else:
        reply_string = "You need to Start the game first"
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)


def CreateGame(parameters, session_url):
    player_color = parameters['Color'] if parameters['Color'] else random.choice(PIECE_COLOR)
    engine_level = parameters['Level'] if parameters['Level'] else 5
    board = chess_engine.create_game()
    delete_row_in_database(session_url=session_url)  # delete if exists in database
    game = Games(session_url=session_url, board=board, engine_level=engine_level, player_color=player_color)
    session = Session()
    session.add(game)
    session.commit()
    session.close()
    if player_color == 'black':
        engine_move, engine_board = chess_engine.let_the_engine_play(engine_level=engine_level, board=board)
        update_board_in_data_base(session_url=session_url, new_board=engine_board)
        reply_string = "Great!! The Game Started. and you are playing with {0} pieces and my first move is {1}".format(player_color, engine_move)
    else:
        reply_string = "Great!! The Game Started. and you are playing with {0} pieces, It's your Move".format(player_color)
    reply = {"fulfillmentText": reply_string}
    return jsonify(reply)