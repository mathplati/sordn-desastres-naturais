"""
Algoritmo de Programação Dinâmica para alocação ótima de recursos limitados.
Maximiza a mitigação total de risco considerando retornos decrescentes por zona.
"""

from typing import List, Dict, Tuple
from models.graph import Graph
import pandas as pd
import math


def _mitigation_value(pop: int, risco: int, teams: int) -> float:
    """
    Função de valor de mitigação com retornos decrescentes (concava).
    Isso faz com que alocar todas as equipes na zona mais urgente NÃO seja sempre ótimo.
    Escala ajustada para números mais amigáveis na demonstração.
    """
    if teams <= 0:
        return 0.0
    base = (pop * risco) / 950.0
    diminishing = math.log(1 + teams * 1.15)
    return round(base * diminishing, 1)


def dp_optimal_allocation(
    graph: Graph,
    df_locations: pd.DataFrame,
    total_teams: int,
    max_per_zone: int = 4,
    hub_id: str = "hub_principal"
) -> Tuple[List[Dict], float, List[float]]:
    """
    Programação Dinâmica (knapsack-like com retornos decrescentes).
    dp[i][j] = máxima mitigação usando as primeiras i zonas com exatamente j equipes.

    Retorna:
    - Lista de alocações ótimas por zona
    - Mitigação total ótima
    - Lista dp[total_teams] para análise de sensibilidade
    """
    affected = df_locations[
        (~df_locations['eh_abrigo']) & (df_locations['id'] != hub_id)
    ].reset_index(drop=True)

    n_zones = len(affected)
    if n_zones == 0:
        return [], 0.0, []

    INF = float('-inf')
    dp = [[INF] * (total_teams + 1) for _ in range(n_zones + 1)]
    dp[0][0] = 0.0

    choice = [[-1] * (total_teams + 1) for _ in range(n_zones + 1)]

    for z in range(n_zones):
        pop = int(affected.loc[z, 'populacao'])
        risco = int(affected.loc[z, 'nivel_risco'])
        zone_id = affected.loc[z, 'id']

        for t in range(total_teams + 1):
            if dp[z][t] == INF:
                continue

            for x in range(max_per_zone + 1):
                if t + x > total_teams:
                    break
                val = _mitigation_value(pop, risco, x)
                new_val = dp[z][t] + val

                if new_val > dp[z + 1][t + x]:
                    dp[z + 1][t + x] = new_val
                    choice[z + 1][t + x] = x

    best_t = max(range(total_teams + 1), key=lambda t: dp[n_zones][t])
    best_mitigation = dp[n_zones][best_t]

    allocations = []
    t_remaining = best_t
    for z in range(n_zones, 0, -1):
        x = choice[z][t_remaining]
        if x > 0:
            pop = int(affected.loc[z-1, 'populacao'])
            risco = int(affected.loc[z-1, 'nivel_risco'])
            val = _mitigation_value(pop, risco, x)
            allocations.append({
                'zona_id': affected.loc[z-1, 'id'],
                'nome': affected.loc[z-1, 'nome'],
                'equipes_alocadas': x,
                'mitigacao_estimada': round(val, 1)
            })
        t_remaining -= x

    allocations.reverse()

    mitigation_by_teams = [round(dp[n_zones][t], 1) if dp[n_zones][t] != INF else 0.0 for t in range(total_teams + 1)]

    return allocations, round(best_mitigation, 1), mitigation_by_teams