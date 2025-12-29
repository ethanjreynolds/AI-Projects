import math

def num_placements_entire(n):
    sq = n*n
    num = int(math.factorial(sq)/(math.factorial(sq-n) * math.factorial(n)))
    return num

def num_placements_one_in_row(n):
    num = n ** n
    return num

def n_queens_valid(board):
    for var in range(len(board)):
        left = board[var]
        middle = board[var]
        right = board[var]
        for compare in range(var + 1, len(board)):
            left -= 1
            right += 1
            if board[compare] == middle:
                return False
            if left >= 0 and board[compare] == left:
                return False
            if right < len(board) and board[compare] == right:
                return False
    return True

def n_queens_helper(n, board):
    row = len(board)
    if row == n:
        yield board.copy()
    else:
        for col in range(n):
            trunum = True
            for r in range(row):
                if col == board[r]:
                    trunum = False
                if abs(col - board[r]) == (row - r):
                    trunum = False
            if trunum == True:
                board.append(col)
                yield from n_queens_helper(n, board)
                board.pop()

def n_queens_solutions(n):
    yield from n_queens_helper(n, [])
