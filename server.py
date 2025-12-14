"""
server_extended.py - Serveur HTTP avec gestion des algorithmes de graphes
"""

import os
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import database
import algorithms

# Configuration
PORT = 8000
PUBLIC_DIR = "public"

class WasteGraphHandler(http.server.SimpleHTTPRequestHandler):
    """Gestionnaire personnalisé avec algorithmes de graphes"""
    
    def __init__(self, *args, **kwargs):
        self.directory = PUBLIC_DIR
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Route pour tester les algorithmes
        if parsed_path.path == '/api/algorithms/test':
            self.handle_test_algorithms()
        else:
            # Servir les fichiers statiques
            super().do_GET()
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/save':
            self.handle_save()
        elif parsed_path.path == '/api/dijkstra':
            self.handle_dijkstra()
        elif parsed_path.path == '/api/color':
            self.handle_color()
        elif parsed_path.path == '/api/validate':
            self.handle_validate()
        elif parsed_path.path == '/api/paths':
            self.handle_all_paths()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Ajouter les headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def handle_test_algorithms(self):
        """Tester les algorithmes avec des données de test"""
        try:
            # Données de test
            test_nodes = [
                {'id': 'A', 'x': 100, 'y': 100},
                {'id': 'B', 'x': 200, 'y': 100},
                {'id': 'C', 'x': 150, 'y': 200},
                {'id': 'D', 'x': 300, 'y': 150}
            ]
            
            test_edges = [
                {'u': 'A', 'v': 'B', 'w': 10},
                {'u': 'A', 'v': 'C', 'w': 15},
                {'u': 'B', 'v': 'C', 'w': 5},
                {'u': 'B', 'v': 'D', 'w': 20},
                {'u': 'C', 'v': 'D', 'w': 10}
            ]
            
            # Tester Dijkstra
            dijkstra_result = algorithms.GraphAlgorithms.dijkstra(
                test_nodes, test_edges, 'A', 'D'
            )
            
            # Tester le coloriage
            coloring_result = algorithms.GraphAlgorithms.color_graph(
                test_nodes, test_edges
            )
            
            # Tester la validation
            validation_result = algorithms.GraphAlgorithms.validate_graph(
                test_nodes, test_edges
            )
            
            response = {
                'status': 'success',
                'test_data': {
                    'nodes': test_nodes,
                    'edges': test_edges
                },
                'algorithms': {
                    'dijkstra': dijkstra_result,
                    'coloring': coloring_result,
                    'validation': validation_result
                }
            }
            
            self.send_json_response(200, response)
            
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def handle_dijkstra(self):
        """Gérer la requête Dijkstra"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'src' in data and 'dst' in data and 'nodes' in data and 'edges' in data:
                result = algorithms.GraphAlgorithms.dijkstra(
                    data['nodes'],
                    data['edges'],
                    data['src'],
                    data['dst']
                )
                self.send_json_response(200, result)
            else:
                self.send_json_response(400, {
                    'error': 'Données manquantes',
                    'required': ['src', 'dst', 'nodes', 'edges']
                })
                
        except json.JSONDecodeError:
            self.send_json_response(400, {'error': 'JSON invalide'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def handle_color(self):
        """Gérer la requête de coloriage"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'nodes' in data and 'edges' in data:
                result = algorithms.GraphAlgorithms.color_graph(
                    data['nodes'],
                    data['edges']
                )
                self.send_json_response(200, {'coloring': result})
            else:
                self.send_json_response(400, {
                    'error': 'Données manquantes',
                    'required': ['nodes', 'edges']
                })
                
        except json.JSONDecodeError:
            self.send_json_response(400, {'error': 'JSON invalide'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def handle_validate(self):
        """Valider un graphe"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'nodes' in data and 'edges' in data:
                result = algorithms.GraphAlgorithms.validate_graph(
                    data['nodes'],
                    data['edges']
                )
                self.send_json_response(200, result)
            else:
                self.send_json_response(400, {
                    'error': 'Données manquantes',
                    'required': ['nodes', 'edges']
                })
                
        except json.JSONDecodeError:
            self.send_json_response(400, {'error': 'JSON invalide'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def handle_all_paths(self):
        """Trouver tous les chemins"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'src' in data and 'dst' in data and 'nodes' in data and 'edges' in data:
                max_paths = data.get('max_paths', 10)
                
                result = algorithms.GraphAlgorithms.find_all_paths(
                    data['nodes'],
                    data['edges'],
                    data['src'],
                    data['dst'],
                    max_paths
                )
                self.send_json_response(200, {'paths': result})
            else:
                self.send_json_response(400, {
                    'error': 'Données manquantes',
                    'required': ['src', 'dst', 'nodes', 'edges']
                })
                
        except json.JSONDecodeError:
            self.send_json_response(400, {'error': 'JSON invalide'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def handle_save(self):
        """Gérer la sauvegarde d'un graphe"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'name' in data and 'nodes' in data and 'edges' in data:
                graph_id = database.save_graph(
                    data['name'],
                    data['nodes'],
                    data['edges']
                )
                if graph_id:
                    self.send_json_response(200, {
                        'id': graph_id, 
                        'message': 'Graph saved successfully',
                        'name': data['name']
                    })
                else:
                    self.send_json_response(500, {'error': 'Failed to save graph'})
            else:
                self.send_json_response(400, {'error': 'Missing data'})
                
        except json.JSONDecodeError:
            self.send_json_response(400, {'error': 'Invalid JSON'})
        except Exception as e:
            self.send_json_response(500, {'error': str(e)})
    
    def send_json_response(self, status_code, data):
        """Envoyer une réponse JSON"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Personnaliser les logs"""
        print(f"[{self.address_string()}] {format % args}")

def main():
    """Fonction principale"""
    # Initialiser la base de données
    print("🔧 Initialisation de la base de données...")
    if database.init_database():
        print("✅ Base de données prête")
    else:
        print("⚠️  Erreur lors de l'initialisation de la base de données")
    
    # Tester les algorithmes
    print("🧪 Test des algorithmes...")
    try:
        test_nodes = [{'id': 'A', 'x': 0, 'y': 0}, {'id': 'B', 'x': 10, 'y': 10}]
        test_edges = [{'u': 'A', 'v': 'B', 'w': 5}]
        
        result = algorithms.GraphAlgorithms.dijkstra(test_nodes, test_edges, 'A', 'B')
        print(f"✅ Dijkstra test: {result}")
        
        coloring = algorithms.GraphAlgorithms.color_graph(test_nodes, test_edges)
        print(f"✅ Coloring test: {coloring}")
        
    except Exception as e:
        print(f"⚠️  Test des algorithmes échoué: {e}")
    
    # Démarrer le serveur
    print(f"\n🌐 Démarrage du serveur sur le port {PORT}...")
    print(f"📁 Servant les fichiers depuis: {os.path.abspath(PUBLIC_DIR)}")
    print(f"🚀 Ouvrez votre navigateur à: http://localhost:{PORT}")
    print("💾 Fonctionnalités disponibles:")
    print("   • POST /api/save - Sauvegarder un graphe")
    print("   • POST /api/dijkstra - Calculer le plus court chemin")
    print("   • POST /api/color - Générer un planning de collecte")
    print("   • POST /api/validate - Valider un graphe")
    print("   • POST /api/paths - Trouver tous les chemins")
    print("   • GET /api/algorithms/test - Tester les algorithmes")
    print("\n🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    
    try:
        with socketserver.TCPServer(("", PORT), WasteGraphHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()