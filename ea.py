import random

from models import Chromosome


def generate_random_chromosome(network, routing_type):
    flows = {}
    for d in network.demands:
        gene = [0] * len(d.paths)

        if routing_type == "bifurcated":
            # rozrzucanie po 1 jednostce
            remaining_volume = d.volume
            while remaining_volume > 0:
                path_idx = random.randint(0, len(d.paths) - 1)
                gene[path_idx] += 1
                remaining_volume -= 1

        elif routing_type == "single_path":
            # cały wolumen ląduje na jednej wylosowanej ścieżce
            path_idx = random.randint(0, len(d.paths) - 1)
            gene[path_idx] = d.volume

        flows[d.id] = gene
    return Chromosome(flows)


def select_parents(population, method="random"):
    """Wybór pary rodziców zgodnie z wytycznymi do raportu R-1."""
    N = len(population)

    if method == "random":
        # Opcja (i): oba chromosomy wybierane losowo
        return random.choice(population), random.choice(population)

    elif method == "best_and_rank":
        # Opcja (ii): X najlepszy, Y z rozkładu p(n) (proporcjonalnie do rangi)
        p1 = population[0]  # Zakładamy, że populacja jest już posortowana
        weights = [N - i for i in range(N)]  # Wagi: N, N-1, ..., 1
        p2 = random.choices(population, weights=weights, k=1)[0]
        return p1, p2

    elif method == "rank_proportional":
        # Opcja (iii): oba z rozkładu p(n) (proporcjonalnie do rangi)
        weights = [N - i for i in range(N)]
        p1 = random.choices(population, weights=weights, k=1)[0]
        p2 = random.choices(population, weights=weights, k=1)[0]
        return p1, p2


def crossover(parent1, parent2, network):
    # (Bez zmian)
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


def mutate(chromosome, network, p, q, routing_type, method="swap"):
    if random.random() > p:
        return chromosome
    mutated_flows = {d_id: list(gene) for d_id, gene in chromosome.flows.items()}

    for d in network.demands:
        if random.random() <= q:
            gene = mutated_flows[d.id]

            if routing_type == "bifurcated":
                # Twój obecny kod
                active_paths = [i for i, flow in enumerate(gene) if flow > 0]
                if active_paths:
                    source_path = random.choice(active_paths)
                    target_path = random.randint(0, len(d.paths) - 1)
                    gene[source_path] -= 1
                    gene[target_path] += 1

            elif routing_type == "single_path":
                # Przeniesienie całego ruchu na inną ścieżkę
                current_path = next(i for i, flow in enumerate(gene) if flow > 0)
                available_paths = [i for i in range(len(d.paths)) if i != current_path]

                if available_paths:
                    new_path = random.choice(available_paths)
                    gene[new_path] = gene[current_path]
                    gene[current_path] = 0

    return Chromosome(mutated_flows)


def run_ea(
    network,
    problem_type,
    routing_type,
    N=20,
    K=10,
    p=0.1,
    q=0.1,
    max_generations=50,
    sel_method="random",
    mut_method="swap",
):
    population = [generate_random_chromosome(network, routing_type) for _ in range(N)]
    for chromo in population:
        chromo.evaluate(network, problem_type)

    population.sort(key=lambda x: x.fitness)
    trajectory = []

    best_overall_fitness = float("inf")
    convergence_gen = 0  # Śledzenie iteracji, w której znaleziono najlepsze rozwiązanie

    for gen in range(max_generations):
        current_best_fitness = population[0].fitness
        trajectory.append(current_best_fitness)

        # Aktualizacja punktu zbieżności
        if current_best_fitness < best_overall_fitness:
            best_overall_fitness = current_best_fitness
            convergence_gen = gen

        O = []
        for _ in range(K):
            p1, p2 = select_parents(population, method=sel_method)
            o1, o2 = crossover(p1, p2, network)
            O.extend([o1, o2])

        for i in range(len(O)):
            O[i] = mutate(O[i], network, p, q, routing_type, method=mut_method)
            O[i].evaluate(network, problem_type)

        O.sort(key=lambda x: x.fitness)

        population.extend(O)
        population.sort(key=lambda x: x.fitness)
        population = population[:N]

    trajectory.append(population[0].fitness)

    # Zwracamy dodatkowy parametr: iterację zbieżności
    return population[0], trajectory, convergence_gen
