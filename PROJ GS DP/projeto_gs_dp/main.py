"""
Sistema de Otimização de Resposta a Desastres Naturais (SORDN)
Projeto para disciplina de Estruturas de Dados e Algoritmos - GS Dynamic Programming

Uso:
    python main.py
"""

import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.graph import Graph
from utils.data_loader import load_disaster_scenario, get_shelters, get_affected_zones
from utils.visualization import (
    print_header, print_table_allocations, print_dijkstra_result,
    plot_graph_with_path, plot_allocation_comparison
)
from algorithms.greedy import greedy_resource_allocation
from algorithms.dynamic_programming import dp_optimal_allocation
from algorithms.randomized import monte_carlo_route_reliability


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_welcome():
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   SISTEMA DE OTIMIZAÇÃO DE RESPOSTA A DESASTRES NATURAIS (SORDN)     ║
║   Tema: Desastres Naturais e Gestão de Riscos                        ║
║   Disciplina: Estruturas de Dados e Algoritmos - 2º Semestre         ║
╚══════════════════════════════════════════════════════════════════════╝

Este sistema demonstra:
  • Modelagem de rede espacial com GRAFOS
  • Algoritmo de caminho mínimo: DIJKSTRA
  • Algoritmo guloso: Priorização de recursos
  • Programação Dinâmica: Alocação ótima com retornos decrescentes
  • Algoritmo randomizado: Simulação Monte Carlo de confiabilidade

Dados: Cenário sintético realista inspirado em regiões brasileiras propensas
       a enchentes e deslizamentos (populações e distâncias baseadas em dados públicos).
""")


def select_zone(prompt: str, valid_ids: list, graph: Graph) -> Optional[str]:
    print(f"\n{prompt}")
    for i, zid in enumerate(valid_ids, 1):
        name = graph.nodes[zid]['nome']
        print(f"  {i}. {name} ({zid})")
    try:
        choice = int(input("\nEscolha o número: ").strip())
        if 1 <= choice <= len(valid_ids):
            return valid_ids[choice - 1]
    except ValueError:
        pass
    print("Seleção inválida.")
    return None


def run_evacuation_route(graph: Graph):
    print_header("1. ROTA DE EVACUAÇÃO ÓTIMA (Dijkstra)")

    shelters = get_shelters(graph)
    affected = get_affected_zones(graph, min_risk=5)

    print("Zonas afetadas disponíveis:")
    start = select_zone("Selecione a zona de ORIGEM (afetada):", affected, graph)
    if not start:
        return

    print("\nAbrigos disponíveis:")
    goal = select_zone("Selecione o ABRIGO de destino:", shelters, graph)
    if not goal:
        return

    path, cost = graph.dijkstra(start, goal)
    print_dijkstra_result(path, cost, graph, start, goal)

    if path:
        resp = input("Deseja visualizar o grafo com a rota destacada? (s/n): ").lower().strip()
        if resp == 's':
            try:
                plot_graph_with_path(graph, path=path, title="Rota de Evacuação Ótima - Dijkstra")
            except Exception as e:
                print(f"Erro ao gerar gráfico (matplotlib necessário): {e}")


def run_greedy_allocation(graph: Graph, df_locations):
    print_header("2. ALOCAÇÃO GULOSA DE RECURSOS")
    total = int(input("Quantas equipes de resgate disponíveis? (ex: 12): ").strip() or "12")

    allocations, total_mit = greedy_resource_allocation(graph, df_locations, total_teams=total)
    print_table_allocations(allocations, "ALOCAÇÃO GULOSA (Prioridade por Urgência)")

    print(f"Total de mitigação estimada (guloso): {total_mit}")
    return allocations


def run_dp_allocation(graph: Graph, df_locations):
    print_header("3. ALOCAÇÃO ÓTIMA COM PROGRAMAÇÃO DINÂMICA")
    total = int(input("Quantas equipes de resgate disponíveis? (ex: 12): ").strip() or "12")

    allocations, best_mit, mitigation_curve = dp_optimal_allocation(
        graph, df_locations, total_teams=total
    )
    print_table_allocations(allocations, "ALOCAÇÃO ÓTIMA (Programação Dinâmica)")

    print(f"Melhor mitigação total encontrada pela DP: {best_mit}")
    print("\n[INFO] A DP considera retornos decrescentes → distribui equipes de forma mais equilibrada que o guloso puro.")
    return allocations, mitigation_curve


def run_monte_carlo(graph: Graph):
    print_header("4. SIMULAÇÃO MONTE CARLO - CONFIABILIDADE DE ROTAS (Randomizado)")

    shelters = get_shelters(graph)
    affected = get_affected_zones(graph, min_risk=5)

    start = select_zone("Selecione zona de ORIGEM para simular evacuação:", affected, graph)
    if not start:
        return
    goal = select_zone("Selecione o ABRIGO de destino:", shelters, graph)
    if not goal:
        return

    print("\nExecutando 800 simulações com 18% de chance de bloqueio aleatório por estrada...")
    result = monte_carlo_route_reliability(graph, start, goal, num_simulations=800, block_probability=0.18)

    print(f"\n📊 RESULTADOS DA SIMULAÇÃO:")
    print(f"   Confiabilidade da rota: {result['confiabilidade_percent']}%")
    print(f"   Tempo médio de evacuação (quando viável): {result['tempo_medio_evacuacao_min']} minutos")
    print(f"   Cenários sem rota viável: {result['cenarios_sem_rota']}")

    print("\n🔴 Arestas mais críticas (usadas com mais frequência em evacuações bem-sucedidas):")
    for c in result['arestas_criticas']:
        print(f"   • {c['aresta']}")
        print(f"     Usada em {c['percentual_dos_sucessos']}% dos cenários de sucesso")

    print(f"\n{result['resumo']}")


def compare_approaches(graph: Graph, df_locations):
    print_header("COMPARAÇÃO: GULOSO vs PROGRAMAÇÃO DINÂMICA")

    total = 12
    print(f"Usando {total} equipes disponíveis para comparação...\n")

    greedy_alloc, g_mit = greedy_resource_allocation(graph, df_locations, total_teams=total)
    dp_alloc, dp_mit, curve = dp_optimal_allocation(graph, df_locations, total_teams=total)

    print(">>> RESULTADO GULOSO:")
    print_table_allocations(greedy_alloc, "Guloso")

    print(">>> RESULTADO PROGRAMAÇÃO DINÂMICA (Ótimo):")
    print_table_allocations(dp_alloc, "Programação Dinâmica")

    print(f"\nMitigação Guloso: {g_mit}  |  Mitigação DP (ótimo): {dp_mit}")
    if dp_mit > g_mit:
        print("✅ A Programação Dinâmica encontrou uma alocação SUPERIOR ao algoritmo guloso!")
    else:
        print("A alocação gulosa foi equivalente ou muito próxima do ótimo.")

    resp = input("\nDeseja ver os gráficos comparativos? (s/n): ").lower().strip()
    if resp == 's':
        try:
            plot_allocation_comparison(greedy_alloc, dp_alloc, curve, total)
        except Exception as e:
            print(f"Erro ao gerar gráficos: {e}")


def main_menu(graph: Graph, df_locations):
    while True:
        print("\n" + "="*70)
        print("MENU PRINCIPAL - Escolha uma opção:")
        print("="*70)
        print("  1. Calcular rota de evacuação ótima (Dijkstra)")
        print("  2. Alocar recursos com algoritmo GULOSO")
        print("  3. Alocar recursos com PROGRAMAÇÃO DINÂMICA (ótimo)")
        print("  4. Simulação Monte Carlo de confiabilidade de rotas (Randomizado)")
        print("  5. Comparar Guloso vs Programação Dinâmica + Gráficos")
        print("  6. Visualizar grafo completo da rede")
        print("  7. Mostrar zonas afetadas e abrigos")
        print("  0. Sair")
        print("-"*70)

        choice = input("Opção: ").strip()

        if choice == "1":
            run_evacuation_route(graph)
        elif choice == "2":
            run_greedy_allocation(graph, df_locations)
        elif choice == "3":
            run_dp_allocation(graph, df_locations)
        elif choice == "4":
            run_monte_carlo(graph)
        elif choice == "5":
            compare_approaches(graph, df_locations)
        elif choice == "6":
            try:
                plot_graph_with_path(graph, path=None, title="Rede Completa de Resposta a Desastres")
            except Exception as e:
                print(f"Erro: {e}. Verifique se matplotlib está instalado.")
        elif choice == "7":
            print_header("ZONAS AFETADAS E ABRIGOS")
            print("Zonas com alto risco:")
            for zid in get_affected_zones(graph):
                a = graph.nodes[zid]
                print(f"  • {a['nome']} | Risco: {a['nivel_risco']} | Pop: {a['populacao']:,}")
            print("\nAbrigos disponíveis:")
            for zid in get_shelters(graph):
                a = graph.nodes[zid]
                print(f"  🛡️ {a['nome']} | Pop: {a['populacao']:,}")
        elif choice == "0":
            print("\nObrigado por usar o SORDN. Boa apresentação!")
            break
        else:
            print("Opção inválida. Tente novamente.")


def main():
    print_welcome()
    input("Pressione ENTER para carregar o cenário de desastre...")

    try:
        graph, df_locations = load_disaster_scenario()
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar dados: {e}")
        print("Verifique se os arquivos data/locations.csv e data/connections.csv existem.")
        sys.exit(1)

    print("\n✅ Cenário carregado com sucesso!")
    print(f"   Zonas: {len(graph)} | Conexões rodoviárias: {len(graph.get_all_edges())}")

    input("\nPressione ENTER para abrir o menu principal...")
    main_menu(graph, df_locations)


if __name__ == "__main__":
    main()