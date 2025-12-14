"""
algorithms.py - Implémentation des algorithmes de graphes en Python
"""

import json
from typing import Dict, List, Tuple, Optional, Set, Any


class GraphAlgorithms:
    """Classe contenant les algorithmes de graphes"""
    
    @staticmethod
    def dijkstra(nodes: List[Dict], edges: List[Dict], src: str, dst: str) -> Dict:
        """
        Implémentation de l'algorithme de Dijkstra pour trouver le chemin le plus court
        
        Args:
            nodes: Liste des nœuds
            edges: Liste des arêtes
            src: Nœud de départ
            dst: Nœud d'arrivée
            
        Returns:
            Dict avec 'path' (liste des nœuds) et 'cost' (coût total)
        """
        # Vérifier si les nœuds existent
        node_ids = {node['id'] for node in nodes}
        src = src.upper()
        dst = dst.upper()
        
        if src not in node_ids:
            return {'path': None, 'cost': float('inf'), 'error': f'Le point {src} n\'existe pas'}
        
        if dst not in node_ids:
            return {'path': None, 'cost': float('inf'), 'error': f'Le point {dst} n\'existe pas'}
        
        # Construire le graphe sous forme de liste d'adjacence
        graph: Dict[str, List[Tuple[str, int]]] = {}
        for node in nodes:
            graph[node['id']] = []
        
        for edge in edges:
            graph[edge['u']].append((edge['v'], edge['w']))
            graph[edge['v']].append((edge['u'], edge['w']))
        
        # Initialisation
        dist: Dict[str, float] = {node['id']: float('inf') for node in nodes}
        prev: Dict[str, Optional[str]] = {node['id']: None for node in nodes}
        dist[src] = 0
        
        unvisited: Set[str] = set(node_ids)
        
        # Algorithme de Dijkstra
        while unvisited:
            # Trouver le nœud non visité avec la distance minimale
            current = None
            min_dist = float('inf')
            for node in unvisited:
                if dist[node] < min_dist:
                    min_dist = dist[node]
                    current = node
            
            if current is None or dist[current] == float('inf'):
                break
            
            unvisited.remove(current)
            
            # Mettre à jour les distances des voisins
            for neighbor, weight in graph[current]:
                if neighbor in unvisited:
                    alt = dist[current] + weight
                    if alt < dist[neighbor]:
                        dist[neighbor] = alt
                        prev[neighbor] = current
        
        # Reconstruire le chemin
        path = []
        current = dst
        while current is not None:
            path.insert(0, current)
            current = prev[current]
        
        # Vérifier si le chemin est valide
        if not path or path[0] != src:
            return {'path': None, 'cost': float('inf'), 'error': 'Aucun chemin trouvé'}
        
        return {
            'path': path,
            'cost': dist[dst],
            'distance': dist[dst]
        }
    
    @staticmethod
    def color_graph(nodes: List[Dict], edges: List[Dict]) -> Dict[str, str]:
        """
        Algorithme de coloriage de graphe pour le planning de collecte
        
        Args:
            nodes: Liste des nœuds
            edges: Liste des arêtes
            
        Returns:
            Dict avec mapping node_id -> jour
        """
        # Construire la liste d'adjacence
        adj: Dict[str, Set[str]] = {}
        for node in nodes:
            adj[node['id']] = set()
        
        for edge in edges:
            adj[edge['u']].add(edge['v'])
            adj[edge['v']].add(edge['u'])
        
        # Jours disponibles
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Weekend"]
        
        # Coloriage
        colors: Dict[str, str] = {}
        
        for node in nodes:
            node_id = node['id']
            used_colors = set()
            
            # Couleurs déjà utilisées par les voisins
            for neighbor in adj[node_id]:
                if neighbor in colors:
                    used_colors.add(colors[neighbor])
            
            # Assigner la première couleur disponible
            for day in days:
                if day not in used_colors:
                    colors[node_id] = day
                    break
            
            # Si aucune couleur n'était disponible, assigner "Weekend"
            if node_id not in colors:
                colors[node_id] = "Weekend"
        
        return colors
    
    @staticmethod
    def validate_graph(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """
        Valider l'intégrité du graphe
        
        Args:
            nodes: Liste des nœuds
            edges: Liste des arêtes
            
        Returns:
            Dict avec les résultats de validation
        """
        errors = []
        warnings = []
        
        # Vérifier les nœuds
        node_ids = set()
        for i, node in enumerate(nodes):
            if not node.get('id'):
                errors.append(f"Node {i} n'a pas d'ID")
            elif node['id'] in node_ids:
                errors.append(f"ID de nœud dupliqué: {node['id']}")
            else:
                node_ids.add(node['id'])
            
            # Vérifier les coordonnées
            if 'x' not in node or 'y' not in node:
                errors.append(f"Node {node.get('id', i)} n'a pas de coordonnées")
        
        # Vérifier les arêtes
        for i, edge in enumerate(edges):
            if 'u' not in edge or 'v' not in edge:
                errors.append(f"Edge {i} n'a pas de points de départ/arrivée")
                continue
            
            if 'w' not in edge:
                errors.append(f"Edge {i} n'a pas de poids")
                continue
            
            u, v = edge['u'], edge['v']
            
            # Vérifier si les nœuds existent
            if u not in node_ids:
                errors.append(f"Edge {i}: le nœud {u} n'existe pas")
            
            if v not in node_ids:
                errors.append(f"Edge {i}: le nœud {v} n'existe pas")
            
            # Vérifier le poids
            if edge['w'] <= 0:
                warnings.append(f"Edge {u}-{v} a un poids non-positif: {edge['w']}")
        
        # Vérifier les composantes connexes
        if nodes and edges:
            # Construire le graphe
            graph = {node['id']: [] for node in nodes}
            for edge in edges:
                if edge['u'] in graph and edge['v'] in graph:
                    graph[edge['u']].append(edge['v'])
                    graph[edge['v']].append(edge['u'])
            
            # Parcours en profondeur pour trouver les composantes
            visited = set()
            components = []
            
            for node_id in graph.keys():
                if node_id not in visited:
                    component = []
                    stack = [node_id]
                    
                    while stack:
                        current = stack.pop()
                        if current not in visited:
                            visited.add(current)
                            component.append(current)
                            stack.extend(neighbor for neighbor in graph[current] 
                                       if neighbor not in visited)
                    
                    components.append(component)
            
            if len(components) > 1:
                warnings.append(f"Le graphe a {len(components)} composantes connexes. "
                              f"Certains nœuds ne sont pas connectés.")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'stats': {
                'nodes': len(nodes),
                'edges': len(edges),
                'node_ids': list(node_ids)
            }
        }
    
    @staticmethod
    def find_all_paths(nodes: List[Dict], edges: List[Dict], src: str, dst: str, 
                       max_paths: int = 10) -> List[Dict]:
        """
        Trouver tous les chemins entre deux nœuds (limité par max_paths)
        
        Args:
            nodes: Liste des nœuds
            edges: Liste des arêtes
            src: Nœud de départ
            dst: Nœud d'arrivée
            max_paths: Nombre maximum de chemins à trouver
            
        Returns:
            Liste de chemins avec leurs coûts
        """
        # Construire le graphe
        graph = {node['id']: [] for node in nodes}
        for edge in edges:
            if edge['u'] in graph and edge['v'] in graph:
                graph[edge['u']].append((edge['v'], edge['w']))
                graph[edge['v']].append((edge['u'], edge['w']))
        
        all_paths = []
        
        def dfs(current: str, target: str, visited: Set[str], 
                path: List[str], cost: int):
            if current == target:
                all_paths.append({
                    'path': path.copy() + [current],
                    'cost': cost
                })
                return
            
            if len(all_paths) >= max_paths:
                return
            
            visited.add(current)
            
            for neighbor, weight in graph[current]:
                if neighbor not in visited:
                    dfs(neighbor, target, visited, 
                        path + [current], cost + weight)
            
            visited.remove(current)
        
        src = src.upper()
        dst = dst.upper()
        
        if src not in graph or dst not in graph:
            return []
        
        dfs(src, dst, set(), [], 0)
        
        # Trier par coût croissant
        all_paths.sort(key=lambda x: x['cost'])
        
        return all_paths[:max_paths]