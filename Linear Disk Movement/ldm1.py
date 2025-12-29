from collections import deque


def find_children(state, length):
    disks = set(state)
    for pos in state:
        if pos + 1 < length and pos + 1 not in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos + 1)
            new.sort()
            yield tuple(new), (pos, pos + 1)
        if pos - 1 >= 0 and pos - 1 not in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos - 1)
            new.sort()
            yield tuple(new), (pos, pos - 1)
        if pos + 2 < length and pos + 2 not in disks and pos + 1 in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos + 2)
            new.sort()
            yield tuple(new), (pos, pos + 2)
        if pos - 2 >= 0 and pos - 2 not in disks and pos - 1 in disks:
            new = list(state)
            new.remove(pos)
            new.append(pos - 2)
            new.sort()
            yield tuple(new), (pos, pos - 2)

def solve_identical_disks(length, n):
    start = tuple(range(n))
    goal = tuple(range(length - n, length))
    if start == goal:
        return []
    frontier = deque()
    visited = set()
    frontier.append((start, []))
    visited.add(start)
    while len(frontier) != 0:
        temp = frontier.popleft()
        state, path = temp
        for child, move in find_children(state, length):
            if child not in visited:
                newpath = path.copy()
                newpath.append(move)
                if child == goal:
                    return newpath
                visited.add(child)
                frontier.append((child, newpath))
    return None

#print(solve_identical_disks(6, 3))

def find_children_distinct(state, length):
    for i, disk in enumerate(state):
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

def solve_distinct_disks(length, n):
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
    frontier = deque()
    visited = set()
    frontier.append((start, []))
    visited.add(start)
    while len(frontier) != 0:
        temp = frontier.popleft()
        state, path = temp
        for child, move in find_children_distinct(state, length):
            if child not in visited:
                newpath = path.copy()
                newpath.append(move)
                if child == goal:
                    return newpath
                visited.add(child)
                frontier.append((child, newpath))
    return None

#print(solve_distinct_disks(5, 3))