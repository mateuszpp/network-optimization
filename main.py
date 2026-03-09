import sys
import math
import argparse
from parser import parse_network_file
from ea import run_ea

def print_detailed_results(best_chromosome, network, problem_type):
    print(f" Wyniki i obliczenia ({problem_type})")
    
    print("\n[1] Zwycięski Chromosom (Przepływy ścieżkowe):")
    for d in network.demands:
        print(f"  Zapotrzebowanie d={d.id} (h={d.volume}): {best_chromosome.flows[d.id]}")
        
    loads = best_chromosome.calculate_link_loads(network)
    
    print(f"\n[2] Obliczenia obciążeń l(e,x) i funkcji celu F(x):")
    
    if problem_type == 'DAP':
        max_overload = -float('inf')
        for link in network.links:
            l_e = loads[link.id]
            c_e = link.capacity
            o_e = l_e - c_e
            if o_e > max_overload:
                max_overload = o_e
            print(f"  Łącze e={link.id}:")
            print(f"    - Obciążenie l(e,x) = {l_e}")
            print(f"    - Pojemność  C(e)   = {c_e}")
            print(f"    - Przeciążenie O(e) = {l_e} - {c_e} = {o_e}")
        print("-" * 30)
        print(f"  MAX Przeciążenie: F(x) = {max_overload}")
        
    elif problem_type == 'DDAP':
        total_cost = 0
        for link in network.links:
            l_e = loads[link.id]
            xi_e = link.cost
            y_e = math.ceil(l_e / network.module_capacity)
            cost_e = y_e * xi_e
            total_cost += cost_e
            
            print(f"  Łącze e={link.id}:")
            print(f"    - Obciążenie l(e,x) = {l_e}")
            print(f"    - Rozmiar modułu M  = {network.module_capacity}")
            print(f"    - Liczba modułów y(e,x) = ceil({l_e}/{network.module_capacity}) = {y_e}")
            print(f"    - Koszt modułu xi(e)= {xi_e}")
            print(f"    - Koszt na łączu    = {y_e} * {xi_e} = {cost_e}")
        print("-" * 30)
        print(f"  CAŁKOWITY KOSZT: F(x) = {total_cost}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algorytm Ewolucyjny dla problemów DAP/DDAP.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dap', action='store_true', help='Uruchom problem DAP')
    group.add_argument('-ddap', action='store_true', help='Uruchom problem DDAP')
    
    parser.add_argument('-f', type=str, required=True, help='Ścieżka do pliku wejściowego (.txt)')
    
    args = parser.parse_args()
    problem_type = 'DAP' if args.dap else 'DDAP'
    filepath = args.f
    
    print(f"Wczytywanie sieci z pliku: {filepath}")
    try:
        network = parse_network_file(filepath)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {filepath}")
        sys.exit(1)
        
    #print(f"Wczytano pomyślnie Łącza: {len(network.links)}, Zapotrzebowania: {len(network.demands)}, M: {network.module_capacity}")
    
    N_param, K_param, p_param, q_param, generations = 20, 10, 0.1, 0.1, 200
    print(f"\nUruchamianie EA dla {problem_type} (N={N_param}, K={K_param}, p={p_param}, q={q_param})")
    
    best_solution = run_ea(network, problem_type, N=N_param, K=K_param, p=p_param, q=q_param, max_generations=generations)
    
    print_detailed_results(best_solution, network, problem_type)