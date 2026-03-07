import math

class Link:
    def __init__(self, id, nodeA, nodeZ, capacity_or_cost):
        self.id = int(id)
        self.nodeA = int(nodeA)
        self.nodeZ = int(nodeZ)
        self.capacity = int(capacity_or_cost) 
        self.cost = int(capacity_or_cost)     

class Demand:
    def __init__(self, id, nodeA, nodeZ, volume):
        self.id = int(id)
        self.nodeA = int(nodeA)
        self.nodeZ = int(nodeZ)
        self.volume = int(volume)
        self.paths = []

class Network:
    def __init__(self, links, demands, module_capacity):
        self.links = links
        self.demands = demands
        self.module_capacity = module_capacity

class Chromosome:
    def __init__(self, flows=None):
        self.flows = flows if flows else {}
        self.fitness = 0.0

    def calculate_link_loads(self, network):
        loads = {link.id: 0 for link in network.links}
        for d in network.demands:
            for p_idx, path in enumerate(d.paths):
                flow = self.flows[d.id][p_idx]
                if flow > 0:
                    for link_id in path:
                        loads[link_id] += flow
        return loads

    def evaluate(self, network, problem_type):
        loads = self.calculate_link_loads(network)
        if problem_type == 'DAP':
            max_overload = -float('inf')
            for link in network.links:
                overload = loads[link.id] - link.capacity
                if overload > max_overload:
                    max_overload = overload
            self.fitness = max_overload
        elif problem_type == 'DDAP':
            total_cost = 0
            for link in network.links:
                modules_needed = math.ceil(loads[link.id] / network.module_capacity)
                total_cost += link.cost * modules_needed
            self.fitness = total_cost