import chess
import chess.engine

STOCK_FISH_LEVEL = {1: 0.1,
                    2: 0.2,
                    3: 0.3,
                    4: 0.4,
                    5: 0.5,
                    6: 0.6,
                    7: 0.7,
                    8: 0.8,
                    9: 0.9,
                    10: 1}


class ChessEngine(object):
    def __init__(self, engine_path):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def create_game(self):
        board = chess.Board()
        return board

    def make_move(self, board, move):
        try:
            board.push_san(move)
        except ValueError:
            raise ValueError
        return board

    def validate_board_status(self, board):
        if board.is_check():
            return 'Check'
        elif board.is_checkmate():
            return 'Checkmate'
        else:
            return ''

    def return_valid_moves(self, board):
        valid_moves = []
        for move in board.legal_moves:
            valid_moves.append(move)
        return valid_moves

    def revert_two_moves(self, board):
        try:
            board.pop()
            board.pop()
        except IndexError:
            raise IndexError
        return board

    def let_the_engine_play(self, engine_level, board):
        result = self.engine.play(board, chess.engine.Limit(time=STOCK_FISH_LEVEL[int(engine_level)]))
        board.push(result.move)
        return result.move, board
        