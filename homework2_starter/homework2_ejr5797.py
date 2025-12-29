############################################################
# CMPSC 442: Informed Search
############################################################

student_name = "Ethan Reynolds"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.

import math
import random
import copy
from collections import deque
from queue import PriorityQueue


############################################################
# Section 1: Tile Puzzle
############################################################

def create_tile_puzzle(rows, cols):
    board = [[r * cols + c for c in range(cols)] for r in range(rows)]
    return TilePuzzle(board)

def iddfs_helper(current, limit, moves, visited):
    if current.is_solved():
        yield list(moves)
        return
    if limit == 0:
        return
    for d, s in current.successors():
        new = tuple(tuple(row) for row in s.board)
        if new not in visited:
            visited.add(new)
            moves.append(d)
            yield from iddfs_helper(s, limit - 1, moves, visited)
            moves.pop()
            visited.remove(new)

class TilePuzzle(object):
    
    # Required
    def __init__(self, board):
        self.board = [list(row) for row in board]
        self.rows = len(board)
        if self.rows > 0:
            self.cols = len(board[0])
        else:
            self.cols = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 0:
                    self.gap = (r, c)
                    break

    def get_board(self):
        return [list(row) for row in self.board]

    def perform_move(self, direction):
        r, c = self.gap
        if direction == 'up':
            dr, dc = -1, 0
        elif direction == 'down':
            dr, dc = 1, 0
        elif direction == 'left':
            dr, dc = 0, -1
        elif direction == 'right':
            dr, dc = 0, 1
            
        if dr != 0 and 0 <= r + dr < self.rows:
            self.board[r][c], self.board[r + dr][c] = self.board[r + dr][c], self.board[r][c]
            self.gap = (r + dr, c)
            return True
        if dc != 0 and 0 <= c + dc < self.cols:
            self.board[r][c], self.board[r][c + dc] = self.board[r][c + dc], self.board[r][c]
            self.gap = (r, c + dc)
            return True
        return False

    def scramble(self, num_moves):
        dir = ["up", "down", "left", "right"]
        for i in range(num_moves):
            self.perform_move(random.choice(dir))

    def is_solved(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != (i * self.cols) + j:
                    return False
        return True

    def copy(self):
        new = copy.deepcopy(self.get_board())
        return TilePuzzle(new)

    def successors(self):
        s = []
        dir = ["up", "down", "left", "right"]
        for d in dir:
            newp = self.copy()
            if newp.perform_move(d):
                s.append((d, newp))
        return s
    
    # Required
    def get_solutions_iddfs(self):
        depth = 0
        start = tuple(tuple(row) for row in self.board)
        visited = set([start])
        while True:
            found = False
            for sol in iddfs_helper(self, depth, [], visited):
                found = True
                yield sol
            if found:
                break
            depth += 1
    
    def manhattan(self):
        dist = 0
        for r in range(self.rows):
            for c in range(self.cols):
                num = self.board[r][c]
                if num != 0:
                    goalr = num // self.rows
                    goalc = num % self.rows
                    dist += abs(r - goalr) + abs(c - goalc)
        return dist

    # Required
    def get_solution_A_star(self):
        start = self.copy()
        pq = PriorityQueue()
        count = 0
        pq.put((start.manhattan(), count, 0, start, []))
        seen = {tuple(tuple(row) for row in start.board): 0}
        
        while not pq.empty():
            og, c, cost, puzzle, path = pq.get()
            if puzzle.is_solved():
                return path
            for d, s in puzzle.successors():
                t = tuple(tuple(row) for row in s.board)
                newcost = cost + 1
                if t not in seen or newcost < seen[t]:
                    seen[t] = newcost
                    count += 1
                    path.append(d)
                    pq.put((newcost + s.manhattan(), count, newcost, s, list(path)))
                    path.pop()
    
# b = [[1,2,3], [4,5,0], [6,7,8]]
# p = TilePuzzle(b)
# solutions = list(p.get_solutions_iddfs())
# print(solutions)
# a = [[1,2,3], [4,5,6], [7,8,0]]
# c = TilePuzzle(a)
# solutions = list(c.get_solutions_iddfs())
# print(solutions)
# c = [[4,1,2], [8,5,3], [7,0,6]]
# d = TilePuzzle(c)
# print(d.manhattan())
# f = [[1,2,3], [4,0,5], [6,7,8]]
# g = TilePuzzle(f)
# print(g.get_solution_A_star())
    
############################################################
# Section 2: Grid Navigation
############################################################

def get_neighbors(node, scene):
    rows = len(scene)
    cols = len(scene[0])
    r, c = node
    dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    neighbors = []
    for x, y in dir:
        if 0 <= r + x < rows and 0 <= c + y < cols and not scene[r + x][c + y]:
            neighbors.append((r + x, c + y))
    return neighbors

def euclid_dist(x, y):
    return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

def find_shortest_path(start, goal, scene):
    rows = len(scene)
    cols = len(scene[0])
    if not (0 <= start[0] < rows and 0 <= start[1] < cols) or not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return None
    if scene[start[0]][start[1]] or scene[goal[0]][goal[1]]:
        return None
    pq = PriorityQueue()
    count = 0
    pq.put((euclid_dist(start, goal), count, 0, start, [start]))
    seen = {start: 0}
    
    while not pq.empty():
        og, c, cost, node, path = pq.get()
        if node == goal:
            return path
        for n in get_neighbors(node, scene):
            newcost = cost + euclid_dist(node, n)
            if n not in seen or newcost < seen[n]:
                seen[n] = newcost
                count += 1
                path.append(n)
                pq.put((newcost + euclid_dist(n, goal), count, newcost, n, list(path)))
                path.pop()
                
# scene = [[False, False, False], 
#           [False, True, False], 
#           [False, True, False], 
#           [False, False, True]]
# print(get_neighbors((1,0), scene))
# print(find_shortest_path((0,0), (3,3), scene))


############################################################
# Section 3: Linear Disk Movement, Revisited
############################################################

def heuristic(state, goal):
    h = 0
    st = list(state)
    go = list(goal)
    for i in range(len(st)):
        current_pos = st[i]
        goal_pos = go[i]
        d = abs(current_pos - goal_pos)
        h += math.ceil(d / 2)
    return h

def find_children_distinct(state, length):
    for i, disk in enumerate(state):
        if disk != -1:
            if i + 1 < length and state[i + 1] == -1:
                new = list(state)
                new[i + 1] = new[i]
                new[i] = -1
                yield tuple(new), (i, i + 1)
            if i - 1 >= 0 and state[i - 1] == -1:
                new = list(state)
                new[i - 1] = new[i]
                new[i] = -1
                yield tuple(new), (i, i - 1)
            if i + 2 < length and state[i + 2] == -1 and state[i + 1] != -1:
                new = list(state)
                new[i + 2] = new[i]
                new[i] = -1
                yield tuple(new), (i, i + 2)
            if i - 2 >= 0 and state[i - 2] == -1 and state[i - 1] != -1:
                new = list(state)
                new[i - 2] = new[i]
                new[i] = -1
                yield tuple(new), (i, i - 2)

def solve_distinct_disks_v2(length, n):
    s = list(range(n))
    for i in range(length - n):
        s.append(-1)
    start = tuple(s)
    g = []
    for i in range(length - n):
        g.append(-1)
    goal = tuple(g + list(range(n))[::-1])
    if start == goal:
        return []
    
    pq = PriorityQueue()
    count = 0
    pq.put((heuristic(start, goal), count, 0, start, []))
    seen = set([start])
    
    while not pq.empty():
        og, c, cost, node, path = pq.get()
        if node == goal:
            return path
        for child, move in find_children_distinct(node, length):
            if child not in seen:
                seen.add(child)
                newcost = cost + 1
                count += 1
                path.append(move)
                pq.put((newcost + heuristic(child, goal), count, newcost, child, list(path)))
                path.pop()
    return None

# print(heuristic((0,1,2), (3,2,1)))
# print(solve_distinct_disks_v2(4,2))
    

############################################################
# Section 4: Dominoes Game
############################################################

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
    
# b = [[False] * 3 for i in range(3)]
# g = DominoesGame(b)
# g.execute_move(0, 1, True)
# print(g.get_best_move(1, False))
        

