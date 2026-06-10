"""
Módulo de modelagem de grafos para o sistema de otimização de resposta a desastres.
Implementa estrutura de grafo customizada + algoritmo de caminho mínimo (Dijkstra).
"""

import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set


class Graph:
    """
    Classe para representar uma rede espacial (cidades/zonas conectadas por estradas).
    Utiliza lista de adjacência para eficiência.
    """

    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.adj: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.edge_list: List[Tuple[str, str, float]] = []

    def add_node(self, node_id: str, **attributes) -> None:
        """Adiciona um nó (cidade/zona) com atributos opcionais."""
        if node_id in self.nodes:
            self.nodes[node_id].update(attributes)
        else:
            self.nodes[node_id] = attributes

    def add_edge(self, u: str, v: str, weight: float, bidirectional: bool = True) -> None:
        """
        Adiciona aresta entre u e v com peso (tempo ou distância).
        bidirectional=True para vias de mão dupla (padrão em redes rodoviárias).
        """
        if u not in self.nodes or v not in self.nodes:
            raise ValueError(f"Nó não encontrado: {u} ou {v}")

        self.adj[u][v] = weight
        self.edge_list.append((u, v, weight))

        if bidirectional:
            self.adj[v][u] = weight
            self.edge_list.append((v, u, weight))

    def get_neighbors(self, node_id: str) -> Dict[str, float]:
        return self.adj.get(node_id, {})

    def dijkstra(
        self,
        start: str,
        goal: str,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None
    ) -> Tuple[Optional[List[str]], float]:
        """
        Implementação do algoritmo de Dijkstra para caminho mínimo.
        Retorna (caminho como lista de nós, custo total) ou (None, inf) se não houver caminho.

        blocked_edges: conjunto de arestas bloqueadas (tuplas ordenadas (u,v) com u < v)
        Usado na simulação Monte Carlo para modelar estradas interditadas por desastre.
        """
        if start not in self.nodes or goal not in self.nodes:
            return None, float('inf')

        if blocked_edges is None:
            blocked_edges = set()

        blocked = set()
        for e in blocked_edges:
            blocked.add(tuple(sorted(e)))

        dist = {node: float('inf') for node in self.nodes}
        dist[start] = 0.0
        prev: Dict[str, Optional[str]] = {node: None for node in self.nodes}
        pq = []
        heapq.heappush(pq, (0.0, start))

        while pq:
            cost, u = heapq.heappop(pq)
            if cost > dist[u]:
                continue
            if u == goal:
                break

            for v, weight in self.adj.get(u, {}).items():
                edge = tuple(sorted([u, v]))
                if edge in blocked:
                    continue
                alt = cost + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))

        if dist[goal] == float('inf'):
            return None, float('inf')

        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()

        return path, dist[goal]

    def get_all_edges(self) -> List[Tuple[str, str, float]]:
        """Retorna lista única de arestas (sem duplicatas bidirecionais)."""
        seen = set()
        unique = []
        for u, v, w in self.edge_list:
            key = tuple(sorted([u, v]))
            if key not in seen:
                seen.add(key)
                unique.append((u, v, w))
        return unique

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"Graph com {len(self.nodes)} nós e {len(self.get_all_edges())} arestas únicas"