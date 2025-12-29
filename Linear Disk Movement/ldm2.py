import math
import random
import copy
from queue import PriorityQueue

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