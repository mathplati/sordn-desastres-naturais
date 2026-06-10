Integrantes:
Gabriel Machado Belardino – 550121
Matheus Aparecido Rocha Plati – 559813
Gustavo Pandolfo Meroni – 560271
Gustavo Neri Santos – 560239
Gustavo Franco Tárano - 559616


# Sistema de Otimização de Resposta a Desastres Naturais (SORDN)

## 📋 Descrição do Projeto

O **SORDN** é uma aplicação Python completa que modela uma rede espacial de zonas urbanas e rurais afetadas por desastres naturais (enchentes e deslizamentos) e otimiza a resposta de emergência usando conceitos avançados de **Estruturas de Dados e Algoritmos**.

O sistema permite:
- Calcular rotas de evacuação mais rápidas
- Priorizar e alocar recursos limitados de forma inteligente
- Avaliar a confiabilidade das rotas sob condições de incerteza (estradas bloqueadas)

## 🎯 Objetivo da Solução

Demonstrar como algoritmos clássicos de grafos e otimização podem ser aplicados em um problema real de **economia espacial e gestão de riscos**, gerando ganhos de eficiência, redução de tempo de resposta e melhor alocação de recursos escassos durante desastres.

## 🗺️ Tema Escolhido

**Desastres Naturais e Gestão de Riscos** (com foco em otimização de rotas de evacuação e alocação de recursos de emergência).

O tema foi escolhido por sua relevância social, forte componente espacial (grafos de transporte) e pela possibilidade de aplicar todos os tipos de algoritmos exigidos de forma coesa e demonstrável.

## 📊 Fonte dos Dados Utilizados

Os dados são **sintéticos mas realistas**, construídos com base em:
- Populações aproximadas de municípios/regiões brasileiras propensas a desastres (inspirado em eventos recentes no Sul e Sudeste)
- Distâncias e tempos de viagem baseados em rotas rodoviárias reais (fontes públicas como Google Maps / OpenStreetMap para regiões de exemplo)
- Níveis de risco modelados a partir de características geográficas típicas (áreas baixas = enchente, encostas = deslizamento)

Arquivos:
- `data/locations.csv` — 8 zonas com população, nível de risco, se é abrigo e coordenadas aproximadas
- `data/connections.csv` — 16 conexões rodoviárias bidirecionais com distância e tempo estimado

Em um cenário de produção, os dados poderiam vir de APIs públicas (IBGE, INPE, OpenStreetMap via osmnx, etc.).

## 🧠 Algoritmos Implementados

### 1. Grafos + Algoritmo de Caminho Mínimo: **Dijkstra**
- **Arquivo:** `models/graph.py`
- Modelagem: Nós = zonas/cidades, Arestas = estradas com peso = tempo de viagem em minutos
- Implementação completa do Dijkstra com heap (prioridade) + reconstrução de caminho
- Uso: Calcular rota de evacuação mais rápida de uma zona afetada até o abrigo mais próximo ou escolhido

### 2. Algoritmo Guloso (Greedy)
- **Arquivo:** `algorithms/greedy.py`
- Heurística: Priorizar zonas com maior score de urgência = `(população × nível_risco) / tempo_até_hub`
- Aloca equipes começando pelas zonas mais críticas primeiro (até limite por zona)
- Rápido e intuitivo, mas não garante ótimo global quando há retornos decrescentes

### 3. Programação Dinâmica (DP)
- **Arquivo:** `algorithms/dynamic_programming.py`
- Problema: Alocação ótima de equipes limitadas maximizando mitigação total de risco
- Abordagem: DP tipo "knapsack com múltiplas escolhas por grupo (zona)"
- Função de valor com **retornos decrescentes** (logarítmica) → alocar tudo na zona mais urgente não é ótimo
- Reconstrói a solução ótima + gera curva de benefício para análise de sensibilidade
- **Demonstra ganho de inteligência computacional** em relação ao guloso

### 4. Algoritmo Randomizado: Simulação Monte Carlo
- **Arquivo:** `algorithms/randomized.py`
- Executa centenas de simulações onde arestas são bloqueadas aleatoriamente (probabilidade de enchente/deslizamento)
- Para cada simulação roda Dijkstra na rede degradada
- Resultados: 
  - Confiabilidade % da rota
  - Tempo médio esperado de evacuação
  - Identificação das **arestas mais críticas** (gargalos da rede)

## 🏗️ Modelagem com Grafos

A rede é modelada como um **grafo não-direcionado ponderado**:

- **Nós (vértices):** Zonas geográficas com atributos:
  - `populacao`, `nivel_risco`, `eh_abrigo`, coordenadas para visualização
- **Arestas:** Conexões rodoviárias com peso = `tempo_min` (mais relevante para emergência que distância pura)
- **Aplicações práticas:**
  - Conectividade entre zonas afetadas e abrigos
  - Rotas (caminho mínimo)
  - Distribuição geográfica de recursos
  - Análise de vulnerabilidade da rede (arestas críticas)

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Pandas** — Manipulação e análise dos dados CSV
- **Matplotlib** — Visualização do grafo + rotas + comparação de alocações (essencial para o vídeo)
- **heapq** + estruturas nativas — Implementação eficiente do Dijkstra
- **Modularização completa** em pacotes: `models/`, `algorithms/`, `utils/`

Não utiliza NetworkX para os algoritmos principais (implementação própria), apenas matplotlib para plots.

## ▶️ Instruções de Execução

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o sistema

```bash
python main.py
```

O programa carrega automaticamente os dados de `data/` e abre um menu interativo em português.

### Menu disponível:
1. Rota de evacuação (Dijkstra)
2. Alocação gulosa de recursos
3. Alocação ótima com Programação Dinâmica
4. Simulação Monte Carlo de confiabilidade
5. Comparação Guloso vs DP + gráficos
6. Visualizar grafo completo
7. Listar zonas e abrigos
0. Sair

### Exemplo de uso para o vídeo:
- Opção 1 → escolher origem e abrigo → mostrar rota + gráfico
- Opção 5 → mostrar que DP > Guloso em alguns casos
- Opção 4 → mostrar análise de risco com arestas críticas

## 👥 Integrantes do Grupo

> **Substitua pelos nomes completos dos integrantes do grupo antes de entregar**

- Integrante 1: [Seu Nome Completo] — [RA]
- Integrante 2: [Nome Completo] — [RA]
- Integrante 3: [Nome Completo] — [RA] (se houver)

---

**Observação importante:** Este projeto foi desenvolvido seguindo rigorosamente todos os requisitos obrigatórios da disciplina:
- ✅ Grafos com aplicação prática (rotas + conectividade)
- ✅ Dijkstra implementado do zero
- ✅ Algoritmo guloso
- ✅ Algoritmo com Programação Dinâmica
- ✅ Algoritmo randomizado (Monte Carlo)
- ✅ Manipulação de arquivos CSV
- ✅ Modularização + classes + funções
- ✅ Tratamento de erros (try/except)
- ✅ Logs e mensagens claras de execução
- ✅ Comparação de desempenho/qualidade entre abordagens (Guloso vs DP)

O código está pronto para ser executado, filmado e enviado ao repositório GitHub.