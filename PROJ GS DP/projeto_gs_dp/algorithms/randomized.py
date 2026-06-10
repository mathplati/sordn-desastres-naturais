"""
Algoritmo Randomizado: Simulação Monte Carlo para análise de confiabilidade de rotas
sob incerteza (estradas bloqueadas aleatoriamente por desastre).
"""

import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from models.graph import Graph


def monte_carlo_route_reliability(
    graph: Graph,
    start: str,
    goal: str,
    num_simulations: int = 800,
    block_probability: float = 0.18
) -> Dict:
    """
    Executa simulação Monte Carlo:
    - Em cada simulação, algumas arestas são "bloqueadas" aleatoriamente (enchente, deslizamento).
    - Roda Dijkstra na rede degradada.
    - Calcula:
        * Confiabilidade (% de simulações com rota viável)
        * Tempo médio de evacuação esperado (condicional ao sucesso)
        * Arestas mais críticas (usadas com mais frequência em rotas bem-sucedidas)
    """
    if start not in graph.nodes or goal not in graph.nodes:
        return {"error": "Nós de origem ou destino inválidos"}

    successful = 0
    total_cost_success = 0.0
    edge_usage = defaultdict(int)
    failed_scenarios = 0

    all_edges = graph.get_all_edges()

    for sim in range(num_simulations):
        blocked = set()
        for u, v, _ in all_edges:
            if random.random() < block_probability:
                blocked.add(tuple(sorted([u, v])))

        path, cost = graph.dijkstra(start, goal, blocked_edges=blocked)

        if path is not None and cost < float('inf'):
            successful += 1
            total_cost_success += cost
            for i in range(len(path) - 1):
                e = tuple(sorted([path[i], path[i + 1]]))
                edge_usage[e] += 1
        else:
            failed_scenarios += 1

    reliability = (successful / num_simulations) * 100 if num_simulations > 0 else 0
    avg_cost = (total_cost_success / successful) if successful > 0 else float('inf')

    critical_edges = sorted(
        [(e, count) for e, count in edge_usage.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    critical_formatted = []
    for (u, v), count in critical_edges:
        name_u = graph.nodes.get(u, {}).get('nome', u)
        name_v = graph.nodes.get(v, {}).get('nome', v)
        critical_formatted.append({
            'aresta': f"{name_u} ↔ {name_v}",
            'vezes_usada': count,
            'percentual_dos_sucessos': round((count / successful) * 100, 1) if successful > 0 else 0
        })

    return {
        'num_simulacoes': num_simulations,
        'probabilidade_bloqueio': block_probability,
        'confiabilidade_percent': round(reliability, 2),
        'tempo_medio_evacuacao_min': round(avg_cost, 1) if avg_cost != float('inf') else None,
        'cenarios_sem_rota': failed_scenarios,
        'arestas_criticas': critical_formatted,
        'resumo': (
            f"Confiabilidade da rota: {reliability:.1f}% | "
            f"Tempo médio esperado: {avg_cost:.1f} min (quando viável)"
        )
    }