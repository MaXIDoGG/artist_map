import networkx as nx
from networkx.readwrite import json_graph

class GraphService:
    def __init__(self, graph_path="data/graph.graphml"):
        self.graph = nx.read_graphml(graph_path)

    def shortest_path(self, artist1, artist2):
        path = nx.shortest_path(self.graph, artist1, artist2)

        return {
            "path": path,
            "degrees": len(path) - 1
        }
    
    def get_full_graph(self):
        return json_graph.node_link_data(self.graph, edges="links")
