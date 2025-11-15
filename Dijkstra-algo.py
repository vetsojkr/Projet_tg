# --- Définition du graphe ---
graph = {
    'A': [('B', 2), ('C', 5)],
    'B': [('A', 2), ('C', 1), ('D', 4)],
    'C': [('A', 5), ('B', 1), ('D', 2)],
    'D': [('B', 4), ('C', 2)]
}

# --- Contrainte C' sur l'arête A->B ---
C_prime_constraint = {('A', 'B'): 7}  # Contrainte spécifique

source = 'A'

# --- Initialisation des distances ---
dist = {node: float('inf') for node in graph}
dist[source] = 0

# --- Ensemble des nœuds non visités ---
unvisited = set(graph.keys())

# --- Début de l'algorithme ---
while unvisited:
    current = None
    for node in unvisited:
        if current is None or dist[node] < dist[current]:
            current = node

    if dist[current] == float('inf'):
        break

    unvisited.remove(current)

    # Mise à jour avec vérification des contraintes
    for neighbor, weight in graph[current]:
        # Vérifier si une contrainte s'applique à cette arête
        edge = (current, neighbor)
        if edge in C_prime_constraint:
            # Utiliser la valeur contrainte au lieu du poids original
            effective_weight = C_prime_constraint[edge]
        else:
            effective_weight = weight
            
        new_dist = dist[current] + effective_weight
        if new_dist < dist[neighbor]:
            dist[neighbor] = new_dist

# --- Résultat final ---
print("Distances avec contraintes C':")
print(dist)
print("Contraintes appliquées:", C_prime_constraint)