import sys
import math
import argparse
import numpy as np
from parser import parse_network_file
from ea import run_ea
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Ustawienie backendu dla Matplotlib (dla lepszej kompatybilności z różnymi systemami)

def print_parsed_network(network):
    """
    Funkcja pomocnicza wypisująca dane wczytane przez parser
    w celu weryfikacji braku halucynacji (błędów wczytywania).
    """

    print(" WERYFIKACJA WCZYTANYCH DANYCH Z PLIKU")
    print("="*50)
    print(f"Rozmiar modułu pojemności (M) = {network.module_capacity}")
    
    print(f"\n--- Łącza (Links) [{len(network.links)}] ---")
    for link in network.links:
        print(f"  ID: {link.id:2} | Węzły: {link.nodeA:2} <-> {link.nodeZ:2} | C(e)/xi(e): {link.capacity}")
        
    print(f"\n--- Zapotrzebowania (Demands) [{len(network.demands)}] ---")
    for d in network.demands:
        print(f"  ID: {d.id:2} | Węzły: {d.nodeA:2} -> {d.nodeZ:2} | h(d): {d.volume:2} | Ścieżki: {d.paths}")
    print("="*50 + "\n")

def print_detailed_results(best_chromosome, network, problem_type):
    print(f" Wyniki i obliczenia ({problem_type})")
    print("\n[1] Zwycięski Chromosom (Przepływy ścieżkowe):")
    for d in network.demands:
        print(f"  Zapotrzebowanie d={d.id} (h={d.volume}): {best_chromosome.flows[d.id]}")

    loads = best_chromosome.calculate_link_loads(network)
    print(f"\n[2] Obliczenia obciążeń l(e,x) i funkcji celu F(x):")

    # if problem_type == 'DAP':
    #     max_overload = -float('inf')
    #     for link in network.links:
    #         l_e = loads[link.id]
    #         c_e = link.capacity
    #         o_e = l_e - c_e
    #         if o_e > max_overload:
    #             max_overload = o_e
    #         print(f"  Łącze e={link.id}: Obciążenie={l_e}, Pojemność={c_e}, Przeciążenie={o_e}")
    #     print("-" * 30)
    #     print(f"  MAX Przeciążenie: F(x) = {max_overload}")

    if problem_type == 'DAP':
        max_overload = -float('inf')
        for link in network.links:
            l_e = loads[link.id]
            # POPRAWKA: liczymy prawdziwą pojemność
            c_e = link.capacity * network.module_capacity 
            o_e = l_e - c_e
            if o_e > max_overload:
                max_overload = o_e
            print(f"  Łącze e={link.id}: Obciążenie={l_e}, Pojemność={c_e}, Przeciążenie={o_e}")
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
            print(f"  Łącze e={link.id}: Obciążenie={l_e}, Moduły={y_e}, Koszt={cost_e}")
        print("-" * 30)
        print(f"  CAŁKOWITY KOSZT: F(x) = {total_cost}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algorytm Ewolucyjny dla problemów DAP/DDAP.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dap', action='store_true', help='Uruchom problem DAP')
    group.add_argument('-ddap', action='store_true', help='Uruchom problem DDAP')

    parser.add_argument('-f', type=str, required=True, help='Ścieżka do pliku wejściowego (.txt)')

    parser.add_argument('--selection', type=str, choices=['random', 'tournament', 'rank'], default='random', help='Metoda doboru rodziców')
    parser.add_argument('--mutation', type=str, choices=['swap', 'reroute'], default='swap', help='Metoda mutacji')
    parser.add_argument('--compare', action='store_true', help='Uruchamia porównanie metod selekcji i generuje wspólny wykres')
    parser.add_argument('--runs', type=int, default=30, help='Liczba uruchomień do uśrednienia w trybie compare')

    args = parser.parse_args()
    problem_type = 'DAP' if args.dap else 'DDAP'
    filepath = args.f

    try:
        network = parse_network_file(filepath)
        # weryfikacja zawartości parsera 
        print_parsed_network(network)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {filepath}")
        sys.exit(1)

    N_param, K_param, p_param, q_param, generations = 50, 25, 0.7, 0.7, 1000

    if args.compare:
        print(f"Uruchamianie trybu porównawczego dla {problem_type} na {generations} generacji (uśrednione z {args.runs} uruchomień)...")
        plt.figure(figsize=(12, 7))
        colors = {'random': 'gray', 'tournament': 'red', 'rank': 'blue'}

        for sel in ['random', 'tournament', 'rank']:
            print(f"\n -> Liczenie dla selekcji: {sel} ({args.runs} powtórzeń)...")
            all_trajectories = []
            final_results = [] # Lista do zbierania wyników końcowych z każdego uruchomienia

            # Pętla wykonująca algorytm określoną liczbę razy
            for run_idx in range(args.runs):
                best_solution, trajectory = run_ea(network, problem_type, N=N_param, K=K_param, p=p_param, q=q_param,
                                       max_generations=generations, sel_method=sel, mut_method='swap')
                all_trajectories.append(trajectory)
                # Ostatni element trajektorii to najlepszy wynik z ostatniej generacji
                final_results.append(trajectory[-1]) 

            # Obliczanie statystyk
            best_fitness = min(final_results)
            worst_fitness = max(final_results)
            mean_fitness = np.mean(final_results)
            
            # Wypisanie statystyk dla danej metody
            print(f"    * Najlepszy wynik końcowy:  {best_fitness}")
            print(f"    * Najgorszy wynik końcowy:  {worst_fitness}")
            print(f"    * Średni wynik końcowy:     {mean_fitness:.2f}")

            # Obliczanie średniej trajektorii do wykresu
            avg_trajectory = np.mean(all_trajectories, axis=0)

            plt.plot(range(len(avg_trajectory)), avg_trajectory, label=f'Selekcja: {sel} (średnia: {mean_fitness:.1f})', color=colors[sel], alpha=0.9, linewidth=2)

        plt.title(f'Porównanie metod selekcji dla problemu {problem_type} (Średnia z {args.runs} uruchomień)')
        plt.xlabel('Generacja')
        plt.ylabel('Średnia wartość funkcji celu (Fitness)')
        plt.legend()
        plt.grid(True)
        print("\nWygenerowano uśredniony wykres. Zamknij okno wykresu, aby zakończyć.")
        plt.show()

    else:
        print(f"Uruchamianie EA ({problem_type}) | Selekcja: {args.selection} | Mutacja: {args.mutation}")
        best_solution, trajectory = run_ea(network, problem_type, N=N_param, K=K_param, p=p_param, q=q_param,
                                           max_generations=generations, sel_method=args.selection, mut_method=args.mutation)

        print_detailed_results(best_solution, network, problem_type)

        plt.figure(figsize=(10, 6))
        plt.plot(range(len(trajectory)), trajectory, marker='o', linestyle='-', color='b')
        plt.title(f'Trajektoria funkcji celu ({problem_type}, Sel: {args.selection}, Mut: {args.mutation})')
        plt.xlabel('Generacja')
        plt.ylabel('Najlepsza wartość funkcji celu (Fitness)')
        plt.grid(True)
        plt.show()