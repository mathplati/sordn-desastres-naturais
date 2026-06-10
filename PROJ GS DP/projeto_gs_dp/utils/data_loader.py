"""
Carregador de dados reais (CSV) para o grafo de rede de resposta a desastres.
"""

import pandas as pd
from typing import Tuple, List
from models.graph import Graph
import os
from pathlib import Path


def _get_data_path(filename: str) -> str:
    """Encontra o caminho correto para os arquivos de dados, independente de onde o script é executado."""
    if os.path.exists(os.path.join("data", filename)):
        return os.path.join("data", filename)
    
    base_dir = Path(__file__).parent.parent
    candidate = base_dir / "data" / filename
    if candidate.exists():
        return str(candidate)
    
    return os.path.join("data", filename)


def load_disaster_scenario(
    locations_path: str = None,
    connections_path: str = None
) -> Tuple[Graph, pd.DataFrame]:
    """
    Carrega os dados de locais e conexões e constrói o grafo.
    Retorna o objeto Graph populado + DataFrame de locais para fácil acesso.
    """
    if locations_path is None:
        locations_path = _get_data_path("locations.csv")
    if connections_path is None:
        connections_path = _get_data_path("connections.csv")

    try:
        df_locations = pd.read_csv(locations_path)
        df_connections = pd.read_csv(connections_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {e}\n"
                                f"Caminho tentado: {locations_path}") from e
    except Exception as e:
        raise RuntimeError(f"Erro ao ler arquivos CSV: {e}") from e

    graph = Graph()

    for _, row in df_locations.iterrows():
        node_id = row['id']
        attributes = {
            'nome': row['nome'],
            'populacao': int(row['populacao']),
            'nivel_risco': int(row['nivel_risco']),
            'eh_abrigo': bool(row['eh_abrigo']),
            'coord_x': float(row['coord_x']),
            'coord_y': float(row['coord_y'])
        }
        graph.add_node(node_id, **attributes)

    for _, row in df_connections.iterrows():
        u = row['from_id']
        v = row['to_id']
        weight = float(row['tempo_min'])
        graph.add_edge(u, v, weight, bidirectional=True)

    print(f"[INFO] Cenário carregado: {len(graph)} zonas | {len(graph.get_all_edges())} conexões rodoviárias")
    return graph, df_locations


def get_shelters(graph: Graph) -> List[str]:
    """Retorna lista de IDs dos abrigos disponíveis."""
    return [nid for nid, attrs in graph.nodes.items() if attrs.get('eh_abrigo', False)]


def get_affected_zones(graph: Graph, min_risk: int = 5) -> List[str]:
    """Retorna zonas com nível de risco acima do limiar (afetadas pelo desastre)."""
    return [
        nid for nid, attrs in graph.nodes.items()
        if attrs.get('nivel_risco', 0) >= min_risk and not attrs.get('eh_abrigo', False)
    ]