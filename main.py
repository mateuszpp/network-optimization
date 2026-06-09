import argparse
import math
import sys
from parser import parse_network_file

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ea import run_ea

matplotlib.use(
    "TkAgg"
)  # Ustawienie backendu dla Matplotlib (dla lepszej kompatybilności z różnymi systemami)


def print_parsed_network(network):
    """
    Funkcja pomocnicza wypisująca dane wczytane przez parser
    w celu weryfikacji braku halucynacji (błędów wczytywania).
    """

    print(" WERYFIKACJA WCZYTANYCH DANYCH Z PLIKU")
    print("=" * 50)
    print(f"Rozmiar modułu pojemności (M) = {network.module_capacity}")

    print(f"\n--- Łącza (Links) [{len(network.links)}] ---")
    for link in network.links:
        print(
            f"  ID: {link.id:2} | Węzły: {link.nodeA:2} <-> {link.nodeZ:2} | C(e)/xi(e): {link.capacity}"
        )

    print(f"\n--- Zapotrzebowania (Demands) [{len(network.demands)}] ---")
    for d in network.demands:
        print(
            f"  ID: {d.id:2} | Węzły: {d.nodeA:2} -> {d.nodeZ:2} | h(d): {d.volume:2} | Ścieżki: {d.paths}"
        )
    print("=" * 50 + "\n")


def print_detailed_results(best_chromosome, network, problem_type):
    print(f" Wyniki i obliczenia ({problem_type})")
    print("\n[1] Zwycięski Chromosom (Przepływy ścieżkowe):")
    for d in network.demands:
        print(
            f"  Zapotrzebowanie d={d.id} (h={d.volume}): {best_chromosome.flows[d.id]}"
        )

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

    if problem_type == "DAP":
        max_overload = -float("inf")
        for link in network.links:
            l_e = loads[link.id]
            # POPRAWKA: liczymy prawdziwą pojemność
            c_e = link.capacity * network.module_capacity
            o_e = l_e - c_e
            if o_e > max_overload:
                max_overload = o_e
            print(
                f"  Łącze e={link.id}: Obciążenie={l_e}, Pojemność={c_e}, Przeciążenie={o_e}"
            )
        print("-" * 30)
        print(f"  MAX Przeciążenie: F(x) = {max_overload}")

    elif problem_type == "DDAP":
        total_cost = 0
        for link in network.links:
            l_e = loads[link.id]
            xi_e = link.cost
            y_e = math.ceil(l_e / network.module_capacity)
            cost_e = y_e * xi_e
            total_cost += cost_e
            print(
                f"  Łącze e={link.id}: Obciążenie={l_e}, Moduły={y_e}, Koszt={cost_e}"
            )
        print("-" * 30)
        print(f"  CAŁKOWITY KOSZT: F(x) = {total_cost}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Algorytm Ewolucyjny dla problemów DAP/DDAP."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-dap", action="store_true", help="Uruchom problem DAP")
    group.add_argument("-ddap", action="store_true", help="Uruchom problem DDAP")

    parser.add_argument(
        "-f", type=str, required=True, help="Ścieżka do pliku wejściowego (.txt)"
    )

    parser.add_argument(
        "--routing",
        type=str,
        choices=["bifurcated", "single_path"],
        default="bifurcated",
        help="Wariant routingu całkowitoliczbowego",
    )

    parser.add_argument(
        "--selection",
        type=str,
        choices=["random", "best_and_rank", "rank_proportional"],
        default="random",
    )

    # Nowa flaga do automatyzacji Raportu R-1
    parser.add_argument(
        "--raport1",
        action="store_true",
        help="Uruchamia automatyczny test 3 zestawów do Raportu R-1 (po 10 przebiegów)",
    )

    args = parser.parse_args()
    problem_type = "DAP" if args.dap else "DDAP"
    routing_type = args.routing
    filepath = args.f

    try:
        network = parse_network_file(filepath)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {filepath}")
        sys.exit(1)

    if args.raport1:
        print("=" * 60)
        print(f" URUCHAMIAM AUTOMATYZACJĘ DLA RAPORTU R-1 ({problem_type})")
        print("=" * 60)

        # Definiujemy 4 zestawy badawcze
        zestawy = [
            {
                "nazwa": "Zestaw 1 (Losowa selekcja)",
                "N": 20,
                "K": 10,
                "p": 0.1,
                "q": 0.1,
                "sel": "random",
            },
            {
                "nazwa": "Zestaw 2 (Najlepszy + Ranga)",
                "N": 20,
                "K": 10,
                "p": 0.1,
                "q": 0.3,
                "sel": "best_and_rank",
            },
            {
                "nazwa": "Zestaw 3 (Ranga + Ranga, Duża Pop)",
                "N": 100,
                "K": 50,
                "p": 0.2,
                "q": 0.2,
                "sel": "rank_proportional",
            },
            {
                "nazwa": "Zestaw 4 (Agresywna Mutacja)",
                "N": 100,
                "K": 50,
                "p": 0.2,
                "q": 0.5,
                "sel": "rank_proportional",
            },
        ]

        runs = 10
        max_gen = 500

        for i, config in enumerate(zestawy):
            print(f"\n--- Badanie: {config['nazwa']} ---")
            print(
                f"Parametry: N={config['N']}, K={config['K']}, p={config['p']}, q={config['q']}, Selekcja={config['sel']}"
            )

            best_fitnesses = []
            convergence_gens = []
            trajectories_to_plot = []

            for run in range(runs):
                best_solution, trajectory, conv_gen = run_ea(
                    network,
                    problem_type,
                    routing_type,
                    N=config["N"],
                    K=config["K"],
                    p=config["p"],
                    q=config["q"],
                    max_generations=max_gen,
                    sel_method=config["sel"],
                    mut_method="swap",
                )

                best_fitnesses.append(trajectory[-1])
                convergence_gens.append(conv_gen)

                # Zapisujemy pierwsze 3 trajektorie do narysowania na wykresie
                if run < 3:
                    trajectories_to_plot.append(trajectory)

            avg_fitness = np.mean(best_fitnesses)
            avg_conv_gen = np.mean(convergence_gens)

            print(f"Wyniki po 10 przebiegach:")
            print(f" -> Uśredniona najlepsza funkcja celu: {avg_fitness:.2f}")
            print(f" -> Uśredniona iteracja zbieżności:    {avg_conv_gen:.1f}")

            # TWORZENIE ODDZIELNEGO WYKRESU DLA OBECNEGO ZESTAWU
            plt.figure(figsize=(8, 5))
            for t_idx, traj in enumerate(trajectories_to_plot):
                plt.plot(range(len(traj)), traj, label=f"Przebieg {t_idx+1}")

            plt.title(f"{config['nazwa']} ({problem_type})")
            plt.xlabel("Generacja")
            plt.ylabel("Wartość funkcji celu (Fitness)")
            plt.grid(True)
            plt.legend()

        print(
            "\nWykresy zostały wygenerowane w osobnych oknach. Przepisz dane do tabel w Raporcie R-1!"
        )
        plt.show()  # Ta komenda na samym końcu otworzy wszystkie 4 okienka naraz

    else:
        # Standardowe, pojedyncze uruchomienie
        print(f"Uruchamianie pojedynczego EA ({problem_type})")
        best_solution, trajectory, conv_gen = run_ea(
            network,
            problem_type,
            routing_type,
            N=20,
            K=10,
            p=0.1,
            q=0.1,
            max_generations=500,
            sel_method=args.selection,
            mut_method="swap",
        )

        print_detailed_results(best_solution, network, problem_type)
        print(f"\nAlgorytm zbiegł się w {conv_gen}. generacji.")

        plt.figure(figsize=(10, 6))
        plt.plot(
            range(len(trajectory)), trajectory, marker="", linestyle="-", color="b"
        )
        plt.title(f"Trajektoria funkcji celu ({problem_type}, Sel: {args.selection})")
        plt.xlabel("Generacja")
        plt.ylabel("Najlepsza wartość funkcji celu")
        plt.grid(True)
        plt.show()

