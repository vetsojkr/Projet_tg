import os
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def get_connection():
    """Établir une connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'wastgraphe_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def init_database():
    """Initialiser la base de données avec les tables nécessaires"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Table pour les graphes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS graphs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table pour les nœuds
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id SERIAL PRIMARY KEY,
                graph_id INTEGER REFERENCES graphs(id) ON DELETE CASCADE,
                node_id VARCHAR(50) NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                UNIQUE(graph_id, node_id)
            )
        """)
        
        # Table pour les arêtes (avec support des contraintes)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id SERIAL PRIMARY KEY,
                graph_id INTEGER REFERENCES graphs(id) ON DELETE CASCADE,
                u VARCHAR(50) NOT NULL,
                v VARCHAR(50) NOT NULL,
                weight INTEGER NOT NULL,
                constraint_distance INTEGER DEFAULT 0,
                original_weight INTEGER,
                UNIQUE(graph_id, u, v),
                CHECK (weight > 0)
            )
        """)
        
        # Création des index pour optimiser les performances
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_nodes_graph_id ON nodes(graph_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_edges_graph_id ON edges(graph_id);
        """)
        
        conn.commit()
        print("✅ Base de données initialisée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def save_graph(name, nodes, edges):
    """Sauvegarder un graphe dans la base de données"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        # Insérer le graphe
        cur.execute(
            "INSERT INTO graphs (name) VALUES (%s) RETURNING id",
            (name,)
        )
        graph_id = cur.fetchone()[0]
        
        # Insérer les nœuds
        for node in nodes:
            cur.execute(
                "INSERT INTO nodes (graph_id, node_id, x, y) VALUES (%s, %s, %s, %s)",
                (graph_id, node['id'], node['x'], node['y'])
            )
        
        # Insérer les arêtes (avec gestion des contraintes)
        for edge in edges:
            # Extraire les informations de contrainte
            constraint_distance = edge.get('constraint', 0)
            original_weight = edge.get('originalWeight', None)
            
            # Calculer le poids final
            if original_weight is not None:
                final_weight = original_weight + constraint_distance
            else:
                final_weight = edge['w']
            
            cur.execute(
                """INSERT INTO edges (graph_id, u, v, weight, constraint_distance, original_weight) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (graph_id, edge['u'], edge['v'], final_weight, constraint_distance, original_weight)
            )
        
        conn.commit()
        return graph_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def drop_database():
    """Supprimer et recréer la base de données (pour le développement)"""
    print("⚠️ ATTENTION: Cette opération va supprimer toutes les données!")
    confirm = input("Êtes-vous sûr? (oui/non): ")
    
    if confirm.lower() != 'oui':
        print("Opération annulée.")
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    try:
        conn.autocommit = True
        cur = conn.cursor()
        
        # Supprimer toutes les tables
        cur.execute("DROP TABLE IF EXISTS edges CASCADE;")
        cur.execute("DROP TABLE IF EXISTS nodes CASCADE;")
        cur.execute("DROP TABLE IF EXISTS graphs CASCADE;")
        
        print("✅ Anciennes tables supprimées")
        
        # Recréer les tables
        init_database()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Menu interactif
    print("=" * 50)
    print("GESTION DE LA BASE DE DONNÉES WASTGRAPH")
    print("=" * 50)
    print("1. Initialiser la base de données")
    print("2. Réinitialiser la base de données (supprimer et recréer)")
    print("3. Tester la connexion")
    print("=" * 50)
    
    choix = input("Votre choix (1-3): ")
    
    if choix == "1":
        if init_database():
            print("✅ Base de données initialisée avec succès!")
        else:
            print("❌ Erreur lors de l'initialisation")
    elif choix == "2":
        drop_database()
    elif choix == "3":
        conn = get_connection()
        if conn:
            print("✅ Connexion à la base de données réussie!")
            conn.close()
        else:
            print("❌ Échec de connexion à la base de données")
    else:
        print("❌ Choix invalide")