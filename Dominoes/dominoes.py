import math
import random
import copy
from queue import PriorityQueue


def make_dominoes_game(rows, cols):
    board = [[False for c in range(cols)] for r in range(rows)]
    return DominoesGame(board)

def evaluate(game, vertical):
    mymoves = 0
    opmoves = 0
    for i in game.legal_moves(vertical):
        mymoves += 1
    for j in game.legal_moves(not vertical):
        opmoves += 1
    return mymoves - opmoves

def alphabeta(game, depth, alpha, beta, maxplayer, currvert, ogvert):
    if depth == 0 or game.game_over(currvert):
        return evaluate(game, ogvert), 1
    leaf = 0
    if maxplayer:
        val = -math.inf
        for move, child in game.successors(currvert):
            num, leafs = alphabeta(child, depth - 1, alpha, beta, False, not currvert, ogvert)
            leaf += leafs
            if num > val:
                val = num
            if val > alpha:
                alpha = val
            if alpha >= beta:
                break
        return val, leaf
    else:
        val = math.inf
        for move, child in game.successors(currvert):
            num, leafs = alphabeta(child, depth - 1, alpha, beta, True, not currvert, ogvert)
            leaf += leafs
            if num < val:
                val = num
            if val < beta:
                beta = val
            if alpha >= beta:
                break
        return val, leaf
            

class DominoesGame(object):

    # Required
    def __init__(self, board):
        self.board = [list(row) for row in board]
        self.rows = len(board)
        if self.rows > 0:
            self.cols = len(board[0])
        else:
            self.cols = 0

    def get_board(self):
        return [list(row) for row in self.board]

    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = False

    def is_legal_move(self, row, col, vertical):
        if row < 0 or col < 0:
            return False
        if vertical is True:
            if row + 1 >= self.rows:
                return False
            if col >= self.cols:
                return False
            if self.board[row][col] is False and self.board[row + 1][col] is False:
                return True
        else:
            if row >= self.rows:
                return False
            if col + 1 >= self.cols:
                return False
            if self.board[row][col] is False and self.board[row][col + 1] is False:
                return True

    def legal_moves(self, vertical):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.is_legal_move(r, c, vertical):
                    yield (r, c)

    def execute_move(self, row, col, vertical):
       self.board[row][col] = True
       if vertical is True:
           self.board[row + 1][col] = True
       else:
           self.board[row][col + 1] = True

    def game_over(self, vertical):
        moves = list(self.legal_moves(vertical))
        if not moves:
            return True
        return False

    def copy(self):
        new = copy.deepcopy(self.get_board())
        return DominoesGame(new)

    def successors(self, vertical):
        for move in self.legal_moves(vertical):
            r, c = move
            s = self.copy()
            s.execute_move(r, c, vertical)
            yield (move, s)

    def get_random_move(self, vertical):
        moves = list(self.legal_moves(vertical))
        if not moves:
            return None
        return random.choice(moves)
        
    # Required
    def get_best_move(self, limit, vertical):
        roots = list(self.legal_moves(vertical))
        if not roots:
            return (None, evaluate(self, vertical), 1)
        
        best_move = None
        best_val = -math.inf
        leafs = 0
        alpha = -math.inf
        beta = math.inf
        
        for move, child in self.successors(vertical):
            val, leaf = alphabeta(child, limit - 1, alpha, beta, False, not vertical, vertical)
            leafs += leaf
            if val > best_val or best_move is None:
                best_val = val
                best_move = move
            if best_val > alpha:
                alpha = best_val
            if alpha >= beta:
                break
        return (best_move, best_val, leafs)