

class BranchAndBoundPath:

    nodes: list[tuple[int, int]]
    total_cost: int
    def __init__(self, nodes: list[tuple[int, int]], total_cost: int):
        self.nodes = nodes
        self.total_cost = total_cost

    def append(self, node: tuple[int, int], cost: int) -> 'BranchAndBoundPath':
        new_nodes = self.nodes.copy()
        new_nodes.append(node)
        new_total_cost = self.total_cost + cost
        return BranchAndBoundPath(new_nodes, new_total_cost)
    
    def len(self) -> int:
        return len(self.nodes)
    
    def cost(self) -> int:
        return self.total_cost
    
    def path(self) -> list[tuple[int, int]]:
        return self.nodes
    
    def __lt__ (self, other: 'BranchAndBoundPath') -> bool:
        return self.total_cost < other.total_cost