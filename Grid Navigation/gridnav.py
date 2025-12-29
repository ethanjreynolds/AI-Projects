import math
import random
import copy
from collections import deque
from queue import PriorityQueue

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