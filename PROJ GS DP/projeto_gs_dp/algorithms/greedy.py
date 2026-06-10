"""
Algoritmo Guloso (Greedy) para priorização de alocação de recursos em desastres.
Seleciona as zonas mais urgentes primeiro (maior impacto populacional + risco).
"""

from typing import List, Dict, Tuple
from models.graph import Graph
import pandas as pd


def compute_urgency_score(
    graph: Graph,
    df_locations: pd.DataFrame,
    hub_id: str = "hub_principal"
) -> pd.DataFrame:
    """
    Calcula score de urgência para cada zona afetada:
    urgencia = (populacao * nivel_risco) / (1 + tempo_min_para_hub)
    Quanto maior, mais prioritário.
    """
    df = df_locations.copy()
    df['urgency'] = 0.0

    for idx, row in df.iterrows():
        node_id = row['id']
        if node_id == hub_id or row['eh_abrigo']:
            continue

        pop = row['populacao']
        risco = row['nivel_risco']

        path, tempo = graph.dijkstra(hub_id, node_id)
        if tempo == float('inf'):
            tempo = 999

        score = (pop * risco) / (1 + tempo)
        df.loc[idx, 'urgency'] = round(score, 2)

    return df.sort_values('urgency', ascending=False)


def greedy_resource_allocation(
    graph: Graph,
    df_locations: pd.DataFrame,
    total_teams: int,
    max_per_zone: int = 4,
    hub_id: str = "hub_principal"
) -> Tuple[List[Dict], float]:
    """
    Algoritmo guloso: aloca recursos priorizando zonas com maior score de urgência.
    Retorna lista de alocações e o valor total estimado de mitigação.
    """
    df_urgency = compute_urgency_score(graph, df_locations, hub_id)

    allocations = []
    remaining = total_teams
    total_mitigation = 0.0

    for _, row in df_urgency.iterrows():
        if remaining <= 0:
            break
        if row['eh_abrigo'] or row['id'] == hub_id:
            continue

        zone_id = row['id']
        pop = row['populacao']
        risco = row['nivel_risco']
        urgency = row['urgency']

        teams_to_assign = min(max_per_zone, remaining)

        mitigation = teams_to_assign * (pop * risco / 10000.0) * (urgency / 50.0)
        total_mitigation += mitigation

        allocations.append({
            'zona_id': zone_id,
            'nome': row['nome'],
            'equipes_alocadas': teams_to_assign,
            'urgencia': urgency,
            'mitigacao_estimada': round(mitigation, 1)
        })
        remaining -= teams_to_assign

    return allocations, round(total_mitigation, 1)