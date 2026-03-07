import random
import copy
from models import Chromosome

def generate_random_chromosome(network):
    flows = {}
    for d in network.demands:
        gene = [0] * len(d.paths)
        remaining_volume = d.volume
        while remaining_volume > 0:
            path_idx = random.randint(0, len(d.paths) - 1)
            gene[path_idx] += 1
            remaining_volume -= 1
        flows[d.id] = gene
    return Chromosome(flows)

def crossover(parent1, parent2, network):
    offspring1_flows = {}
    offspring2_flows = {}
    for d in network.demands:
        if random.random() < 0.5:
            offspring1_flows[d.id] = list(parent1.flows[d.id])
            offspring2_flows[d.id] = list(parent2.flows[d.id])
        else:
            offspring1_flows[d.id] = list(parent2.flows[d.id])
            offspring2_flows[d.id] = list(parent1.flows[d.id])
    return Chromosome(offspring1_flows), Chromosome(offspring2_flows)

def mutate(chromosome, network, p, q):
    if random.random() > p:
        return chromosome 
    mutated_flows = copy.deepcopy(chromosome.flows)
    for d in network.demands:
        if random.random() <= q:
            gene = mutated_flows[d.id]
            active_paths = [i for i, flow in enumerate(gene) if flow > 0]
            if active_paths:
                source_path = random.choice(active_paths)
                target_path = random.randint(0, len(d.paths) - 1)
                gene[source_path] -= 1
                gene[target_path] += 1
    return Chromosome(mutated_flows)

def run_ea(network, problem_type, N=20, K=10, p=0.1, q=0.1, max_generations=50):
    population = [generate_random_chromosome(network) for _ in range(N)]
    for chromo in population:
        chromo.evaluate(network, problem_type)
    population.sort(key=lambda x: x.fitness)
    
    for gen in range(max_generations):
        O = []
        for _ in range(K):
            p1 = random.choice(population)
            p2 = random.choice(population)
            o1, o2 = crossover(p1, p2, network)
            O.extend([o1, o2])
            
        for i in range(len(O)):
            O[i] = mutate(O[i], network, p, q)
            O[i].evaluate(network, problem_type)
            
        population.extend(O)
        population.sort(key=lambda x: x.fitness)
        population = population[:N] 
        
    return population[0]