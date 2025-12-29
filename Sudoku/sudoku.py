from collections import deque


def sudoku_cells():
    return [(r, c) for r in range(9) for c in range(9)]

def sudoku_arcs():
    arcs = []
    for r in range(9):
        for c in range(9):
            cell = (r, c)
            for k in range(9):
                if k != c:
                    arcs.append((cell, (r, k)))
                if k != r:
                    arcs.append((cell, (k, c)))
            br, bc = 3 * (r // 3), 3 * (c // 3)
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    if (rr, cc) != cell:
                        arcs.append((cell, (rr, cc)))
    return arcs

def read_board(path):
    board = {}
    lines = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if s:
                lines.append(s)
    rows = len(lines)
    for r in range(rows):
        line = lines[r]
        cols = len(line)
        for c in range(cols):
            ch = line[c]
            if ch == '*':
                board[(r, c)] = set(range(1, 10))
            else:
                board[(r, c)] = {int(ch)}
    return board

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    def remove_inconsistent_values(self, cell1, cell2):
        removed = False
        b1 = self.board[cell1]
        b2 = self.board[cell2]
        r = set()
        for v in b1:
            allmatch = True
            for w in b2:
                if w != v:
                    allmatch = False
                    break
            if allmatch:
                r.add(v)
        if r:
            for v in r:
                if v in b1:
                    b1.remove(v)
            removed = True
        return removed

    def infer_ac3(self):
        queue = deque(Sudoku.ARCS)
        while queue:
            (cell1, cell2) = queue.popleft()
            if self.remove_inconsistent_values(cell1, cell2):
                if not self.board[cell1]:
                    return False
                for (r, c) in Sudoku.CELLS:
                    if (r, c) != cell1 and (r, c) != cell2:
                        if r == cell1[0] or c == cell1[1] or (r // 3, c // 3) == (cell1[0] // 3, cell1[1] // 3):
                            queue.append(((r, c), cell1))
        return True

    def infer_improved(self):
        diff = True
        while diff:
            diff = False
            if not self.infer_ac3():
                return False

            for r in range(9):
                unit = [(r, c) for c in range(9)]
                for digit in range(1, 10):
                    cs = []
                    found = False
                    for cell in unit:
                        vals = self.board[cell]
                        if len(vals) == 1 and list(vals)[0] == digit:
                            cs = [cell]
                            found = True
                        elif digit in vals and not found:
                            cs.append(cell)
                    if not cs:
                        return False
                    if len(cs) == 1:
                        t = cs[0]
                        vals = self.board[t]
                        if not (len(vals) == 1 and list(vals)[0] == digit):
                            self.board[t] = {digit}
                            diff = True
            
            for c in range(9):
                unit = [(r, c) for r in range(9)]
                for digit in range(1, 10):
                    cs = []
                    found = False
                    for cell in unit:
                        vals = self.board[cell]
                        if len(vals) == 1 and list(vals)[0] == digit:
                            cs = [cell]
                            found = True
                        elif digit in vals and not found:
                            cs.append(cell)
                    if not cs:
                        return False
                    if len(cs) == 1:
                        t = cs[0]
                        vals = self.board[t]
                        if not (len(vals) == 1 and list(vals)[0] == digit):
                            self.board[t] = {digit}
                            diff = True
            
            for br in (0, 3, 6):
                for bc in (0, 3, 6):
                    unit = []
                    for rr in range(br, br + 3):
                        for cc in range(bc, bc + 3):
                            unit.append((rr, cc))
                    for digit in range(1, 10):
                        cs = []
                        found = False
                        for cell in unit:
                            vals = self.board[cell]
                            if len(vals) == 1 and list(vals)[0] == digit:
                                cs = [cell]
                                found = True
                            if digit in vals and not found:
                                cs.append(cell)
                        if not cs:
                            return False
                        if len(cs) == 1:
                            t = cs[0]
                            vals = self.board[t]
                            if not (len(vals) == 1 and list(vals)[0] == digit):
                                self.board[t] = {digit}
                                diff = True
        return True
    
        
# b = read_board("sudoku/hw3-easy.txt")
# c = Sudoku(b).infer_ac3()
# display(b)
# print()
# b = read_board("sudoku/hw3-medium3.txt")
# c = Sudoku(b).infer_improved()
# display(b)