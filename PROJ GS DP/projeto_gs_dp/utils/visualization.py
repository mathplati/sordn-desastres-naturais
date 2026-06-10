"""
Módulo de visualização para o projeto de otimização de resposta a desastres.
Gera tabelas no terminal + gráficos matplotlib (opcional) para o vídeo da apresentação.
"""

import pandas as pd
from typing import List, Dict, Optional
from models.graph import Graph
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_table_allocations(allocations: List[Dict], title: str = "Alocação de Recursos"):
    """Imprime tabela bonita de alocações no terminal."""
    if not allocations:
        print("Nenhuma alocação realizada.")
        return

    print_header(title)
    print(f"{'Zona':<45} {'Equipes':>8} {'Mitigação':>12}")
    print("-" * 70)
    total_teams = 0
    total_mit = 0.0
    for a in allocations:
        print(f"{a['nome']:<45} {a['equipes_alocadas']:>8} {a.get('mitigacao_estimada', 0):>12.1f}")
        total_teams += a['equipes_alocadas']
        total_mit += a.get('mitigacao_estimada', 0)
    print("-" * 70)
    print(f"{'TOTAL':<45} {total_teams:>8} {total_mit:>12.1f}")
    print()


def print_dijkstra_result(path: Optional[List[str]], cost: float, graph: Graph, start: str, goal: str):
    print_header("ROTA DE EVACUAÇÃO ÓTIMA (Dijkstra)")
    if path is None:
        print(f"❌ Não foi possível encontrar rota de {start} para {goal}.")
        return

    names = [graph.nodes[n]['nome'] for n in path]
    print(f"Origem : {graph.nodes[start]['nome']}")
    print(f"Destino: {graph.nodes[goal]['nome']}")
    print(f"Tempo estimado de viagem: {cost:.0f} minutos")
    print("\nCaminho detalhado:")
    for i, node in enumerate(path):
        marker = "🏠" if i == 0 else ("🛡️" if i == len(path)-1 else "→")
        print(f"  {marker} {graph.nodes[node]['nome']}")
    print()


def plot_graph_with_path(
    graph: Graph,
    path: Optional[List[str]] = None,
    title: str = "Rede de Resposta a Desastres - Rotas de Evacuação"
):
    """
    Desenha o grafo com posições geográficas aproximadas + caminho destacado.
    Útil para o vídeo da apresentação.
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    pos = {nid: (attrs['coord_x'], attrs['coord_y']) for nid, attrs in graph.nodes.items()}

    for u, v, w in graph.get_all_edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], 'gray', linewidth=1.5, alpha=0.6, zorder=1)

    for nid, attrs in graph.nodes.items():
        x, y = pos[nid]
        color = '#2ecc71' if attrs.get('eh_abrigo') else '#e74c3c'
        size = 800 + (attrs.get('populacao', 30000) / 150)
        ax.scatter(x, y, s=size, c=color, alpha=0.85, edgecolors='black', linewidths=1.5, zorder=3)

        short_name = attrs['nome'].split('(')[0].strip()[:18]
        ax.annotate(short_name, (x, y), textcoords="offset points", xytext=(0, 12),
                    ha='center', fontsize=9, fontweight='bold')

    if path and len(path) > 1:
        path_x = [pos[n][0] for n in path]
        path_y = [pos[n][1] for n in path]
        ax.plot(path_x, path_y, color='#f39c12', linewidth=4.5, alpha=0.9, zorder=4, label='Rota Ótima (Dijkstra)')
        ax.scatter(path_x, path_y, s=120, c='#f39c12', edgecolors='black', linewidths=2, zorder=5)

    red_patch = mpatches.Patch(color='#e74c3c', label='Zonas Afetadas / Alto Risco')
    green_patch = mpatches.Patch(color='#2ecc71', label='Abrigos / Centros de Recursos')
    ax.legend(handles=[red_patch, green_patch], loc='upper left', fontsize=10)

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Coordenada X (aprox.)", fontsize=10)
    ax.set_ylabel("Coordenada Y (aprox.)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.show()


def plot_allocation_comparison(
    greedy_alloc: List[Dict],
    dp_alloc: List[Dict],
    dp_mitigation_curve: List[float],
    total_teams: int
):
    """Compara alocação Gulosa vs Programação Dinâmica + curva de benefício DP."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Gráfico 1: Barras comparativas por zona
    ax1 = axes[0]
    all_zones = sorted(set([a['nome'][:25] for a in greedy_alloc + dp_alloc]))

    greedy_dict = {a['nome'][:25]: a['equipes_alocadas'] for a in greedy_alloc}
    dp_dict = {a['nome'][:25]: a['equipes_alocadas'] for a in dp_alloc}

    x = np.arange(len(all_zones))
    width = 0.35

    g_vals = [greedy_dict.get(z, 0) for z in all_zones]
    d_vals = [dp_dict.get(z, 0) for z in all_zones]

    bars1 = ax1.bar(x - width/2, g_vals, width, label='Guloso (Greedy)', color='#3498db')
    bars2 = ax1.bar(x + width/2, d_vals, width, label='Programação Dinâmica (Ótimo)', color='#e67e22')

    ax1.set_ylabel('Equipes Alocadas')
    ax1.set_title('Comparação de Alocação de Recursos', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(all_zones, rotation=35, ha='right', fontsize=8)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Gráfico 2: Curva de benefício acumulado da DP
    ax2 = axes[1]
    teams_range = list(range(len(dp_mitigation_curve)))
    ax2.plot(teams_range, dp_mitigation_curve, marker='o', color='#27ae60', linewidth=2.5, markersize=5)
    ax2.fill_between(teams_range, dp_mitigation_curve, alpha=0.2, color='#27ae60')
    ax2.set_xlabel('Total de Equipes Disponíveis')
    ax2.set_ylabel('Mitigação Total de Risco (ótimo)')
    ax2.set_title('Curva de Benefício - Programação Dinâmica', fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()