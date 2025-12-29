import math
import random
import copy
from collections import deque
from queue import PriorityQueue

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