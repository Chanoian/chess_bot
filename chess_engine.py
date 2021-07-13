import chess
import chess.engine
from stockfish import Stockfish

STOCK_FISH_LEVEL = {1: 1,
                    2: 4,
                    3: 6,
                    4: 8,
                    5: 10,
                    6: 12,
                    7: 14,
                    8: 16,
                    9: 18,
                    10: 20}


class ChessEngine(object):
    def __init__(self, engine_path):
        self.stockfish = Stockfish(engine_path)
        #self.stockfish = chess.engine.SimpleEngine.popen_uci(engine_path)

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
        if board.is_checkmate():
            return 'Checkmate'
        elif board.is_check():
            return 'Check'
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
        self.stockfish.set_skill_level(STOCK_FISH_LEVEL[int(engine_level)])
        self.stockfish.set_fen_position(board.fen())
        #result = self.stockfish.play(board, chess.engine.Limit(time=0.1))
        move = self.stockfish.get_best_move_time(1000)
        #move = result.move
        board.push(chess.Move.from_uci(move))
        return move, board
