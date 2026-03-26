from __future__ import annotations

import heapq
import random
from dataclasses import dataclass
from typing import Callable

from core.grid import Grid
from core.path import Path
from core.tiles import Tile
from core.babpath import BranchAndBoundPath


@dataclass(slots=True)
class Agent:
    name: str

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        raise NotImplementedError


class ExampleAgent(Agent):

    def __init__(self):
        super().__init__("Example")


    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        while nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)

            min_dist = min(grid.manhattan(t.pos, goal) for t in neighbors)
            best_tiles = [
                tile for tile in neighbors
                if grid.manhattan(tile.pos, goal) == min_dist
            ]
            best_tile = best_tiles[random.randint(0, len(best_tiles) - 1)]

            nodes.append(best_tile.pos)


        return Path(nodes)


direction_priority = [
    (0,1),
    (1,0),
    (0,-1),
    (-1,0)
]

class DFSAgent(Agent):

    def __init__(self):
        super().__init__("DFS")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        visited = set()
        while nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)
            visited.add((r, c))
            neighbors = [tile for tile in neighbors if tile.pos not in visited]
            if not neighbors:
                nodes.pop()
                continue
            min_cost = min(tile.cost for tile in neighbors)
            best_tiles = [
                tile for tile in neighbors
                if tile.cost == min_cost
            ]

            def direction_index(tile: Tile) -> int:
                dr = tile.row - r
                dc = tile.col - c
                return direction_priority.index((dr, dc))
            
            best_tiles.sort(key=direction_index)
            
            best_tile = best_tiles[0]

            nodes.append(best_tile.pos)

        return Path(nodes)
    
def BaB_search(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int], A_star: bool) -> Path:
        available_paths = []
        heapq.heappush(available_paths, (0, BranchAndBoundPath([start], 0)))
        node_best_cost: dict[tuple[int, int], int] = {}
        while available_paths:
            best_paths = []
            best_cost, current_path = heapq.heappop(available_paths)
            best_paths.append(current_path)
            while available_paths and available_paths[0][0] == best_cost:
                _, path = heapq.heappop(available_paths)
                best_paths.append(path)
            min_len = min(p.len() for p in best_paths)
            absolute_best_paths = [
                p for p in best_paths
                if p.len() == min_len
            ]
            best_paths = [p for p in best_paths if p not in absolute_best_paths]
            current_path = absolute_best_paths.pop(random.randint(0, len(absolute_best_paths) - 1))
            absolute_best_paths.extend(best_paths)
            current_node = current_path.path()[-1]
            if current_node == goal:
                return Path(current_path.path())
            for p in absolute_best_paths:
                if A_star:
                    priority = p.cost() + grid.manhattan(p.path()[-1], goal)
                else:
                    priority = p.cost()
                heapq.heappush(available_paths, (priority, p))
            if current_node in node_best_cost and current_path.cost() > node_best_cost[current_node]:
                continue
            node_best_cost[current_node] = current_path.cost()
            r, c = current_node
            neighbors = grid.neighbors4(r, c)
            neighbors = [tile for tile in neighbors if tile.pos not in current_path.path()]
            for tile in neighbors:
                new_path = current_path.append(tile.pos, tile.cost)
                if A_star:
                    priority = new_path.cost() + grid.manhattan(tile.pos, goal)
                else:
                    priority = new_path.cost()
                heapq.heappush(available_paths, (priority, new_path))

class BranchAndBoundAgent(Agent):

    def __init__(self):
        super().__init__("BranchAndBound")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        return BaB_search(self, grid, start, goal, False)
        


class AStar(Agent):

    def __init__(self):
        super().__init__("AStar")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        return BaB_search(self, grid, start, goal, True)


AGENTS: dict[str, Callable[[], Agent]] = {
    "Example": ExampleAgent,
    "DFS": DFSAgent,
    "BranchAndBound": BranchAndBoundAgent,
    "AStar": AStar
}


def create_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent '{name}'. Available: {', '.join(AGENTS.keys())}")
    return AGENTS[name]()
