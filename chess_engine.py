import chess
import chess.engine

STOCK_FISH_LEVEL = {1:0.1,
                    2:0.2,
                    3:0.3,
                    4:0.4,
                    5:0.5,
                    6:0.6,
                    7:0.7,
                    8:0.8,
                    9:0.9,
                    10:1}


class ChessEngine(object):
    def __init__(self, engine_path):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def create_game(self):
        self.board = chess.Board()
        return self.board

    def make_move(self, board, move):
        try:
            board.push_san(move)
        except ValueError as e :
            raise ValueError
        return board

    def revert_two_moves(self, board):
        try:
            board.pop()
            board.pop()
        except IndexError as e :
            raise e
        return board

    def let_the_engine_play(self, engine_level, board):
        result = self.engine.play(board, chess.engine.Limit(time=STOCK_FISH_LEVEL[engine_level]))
        board.push(result.move)
        return result.move, board

    def return_board(self):
        return self.board


# engine_path = "/home/builder/chess_bot_gcloud/stockfish-11-linux/Linux/stockfish_20011801_x64"
# new = ChessEngine(engine_path=engine_path)
# new.create_game()
# my_board = new.return_board()
# new.make_move(my_board, 'e4')
# print(my_board)
# new.create_game()
# print(new.return_board())
# print(new.let_the_engine_play())
# print(new.return_board())
# new.make_move('d5')
# print(new.return_board())