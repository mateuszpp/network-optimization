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

def select_parents(population, method="random", tournament_size=3):
    """Wybór pary rodziców na podstawie określonej metody."""
    if method == "random":
        return random.choice(population), random.choice(population)

    elif method == "tournament":
        # Losujemy 'tournament_size' osobników i wybieramy z nich tego z najlepszym fitness
        p1 = min(random.sample(population, min(tournament_size, len(population))), key=lambda x: x.fitness)
        p2 = min(random.sample(population, min(tournament_size, len(population))), key=lambda x: x.fitness)
        return p1, p2

    elif method == "rank":
        # Zakładamy, że populacja jest już posortowana (najlepszy na indeksie 0)
        # Rangi: osobnik na indeksie 0 dostaje wagę N, na indeksie 1 wagę N-1, itd.
        ranks = list(range(len(population), 0, -1))
        p1 = random.choices(population, weights=ranks, k=1)[0]
        p2 = random.choices(population, weights=ranks, k=1)[0]
        return p1, p2

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

def mutate(chromosome, network, p, q, method="swap"):
    if random.random() > p:
        return chromosome
    mutated_flows = copy.deepcopy(chromosome.flows)

    for d in network.demands:
        if random.random() <= q:
            gene = mutated_flows[d.id]

            if method == "swap":
                # Metoda z etapu 1: przeniesienie 1 jednostki ruchu
                active_paths = [i for i, flow in enumerate(gene) if flow > 0]
                if active_paths:
                    source_path = random.choice(active_paths)
                    target_path = random.randint(0, len(d.paths) - 1)
                    gene[source_path] -= 1
                    gene[target_path] += 1

            elif method == "reroute":
                # Nowa metoda: przydzielenie całego ruchu dla tego zapotrzebowania do 1 losowej ścieżki
                total_flow = sum(gene)
                new_gene = [0] * len(d.paths)
                target_path = random.randint(0, len(d.paths) - 1)
                new_gene[target_path] = total_flow
                mutated_flows[d.id] = new_gene

    return Chromosome(mutated_flows)

def run_ea(network, problem_type, N=20, K=10, p=0.1, q=0.1, max_generations=50, sel_method="random", mut_method="swap"):
    population = [generate_random_chromosome(network) for _ in range(N)]
    for chromo in population:
        chromo.evaluate(network, problem_type)

    population.sort(key=lambda x: x.fitness)
    trajectory = []

    for gen in range(max_generations):
        trajectory.append(population[0].fitness)

        O = []
        for _ in range(K):
            # Użycie nowej funkcji doboru rodziców
            p1, p2 = select_parents(population, method=sel_method)
            o1, o2 = crossover(p1, p2, network)
            O.extend([o1, o2])

        for i in range(len(O)):
            O[i] = mutate(O[i], network, p, q, method=mut_method)
            O[i].evaluate(network, problem_type)

        O.sort(key=lambda x: x.fitness)

        population.extend(O)
        population.sort(key=lambda x: x.fitness)
        population = population[:N]

    trajectory.append(population[0].fitness)
    return population[0], trajectory
