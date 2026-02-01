import osmnx as ox
import networkx as nx
import folium
from networkx.algorithms.simple_paths import shortest_simple_paths
import os

class SafeRouteEngine:
    def __init__(self, graph_file="nagpur.graphml"):
        self.graph_file = graph_file
        self.G = None
        self.G_simple = None
        self.blocked_edges = set()
        self.load_graph()

    def load_graph(self):
        if os.path.exists(self.graph_file):
            print(f"Loading graph from {self.graph_file}...")
            self.G = ox.load_graphml(self.graph_file)
        else:
            print(f"Graph file {self.graph_file} not found. Downloading Nagpur graph...")
            try:
                self.G = ox.graph_from_place("Nagpur, India", network_type="drive")
                ox.save_graphml(self.G, self.graph_file)
            except Exception as e:
                print(f"Error downloading graph: {e}")
                # Fallback or raise error
                raise
        
        print("Graph loaded.")
        self.simplify_graph()

    def simplify_graph(self):
        self.G_simple = nx.DiGraph()
        for u, v, k, data in self.G.edges(keys=True, data=True):
            if not self.G_simple.has_node(u):
                self.G_simple.add_node(u, **self.G.nodes[u])
            if not self.G_simple.has_node(v):
                self.G_simple.add_node(v, **self.G.nodes[v])

            length = data.get("length", 1)
            if self.G_simple.has_edge(u, v):
                self.G_simple[u][v]["length"] = min(self.G_simple[u][v]["length"], length)
            else:
                self.G_simple.add_edge(u, v, length=length)

        self.G_simple.graph["crs"] = "EPSG:4326"

    def apply_blocked_edges(self):
        G2 = self.G_simple.copy()
        for u, v in self.blocked_edges:
            if G2.has_edge(u, v):
                G2.remove_edge(u, v)
        return G2

    def get_routes(self, start, end, k=4):
        G_safe = self.apply_blocked_edges()

        try:
            start_node = ox.distance.nearest_nodes(G_safe, start[1], start[0])
            end_node = ox.distance.nearest_nodes(G_safe, end[1], end[0])
        except Exception as e:
            print(f"Error finding nearest nodes: {e}")
            return []

        routes = []
        try:
            gen = shortest_simple_paths(G_safe, start_node, end_node, weight="length")
            for i, path in enumerate(gen):
                if i >= k:
                    break
                routes.append(path)
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            print(f"Error finding paths: {e}")
            return []

        return routes

    def block_middle_segment(self, route):
        mid = len(route) // 2
        u = route[mid]
        v = route[mid + 1]
        self.blocked_edges.add((u, v))
        print(f"🚧 Blocked road segment: {u} → {v}")

    def generate_map_html(self, start, end):
        routes = self.get_routes(start, end)
        
        m = folium.Map(location=start, zoom_start=13)
        colors = ["blue", "green", "purple", "orange"]

        if routes:
            for i, r in enumerate(routes):
                color = colors[i % len(colors)]
                coords = [(self.G_simple.nodes[n]["y"], self.G_simple.nodes[n]["x"]) for n in r]
                folium.PolyLine(coords, color=color, weight=5, opacity=0.7, tooltip=f"Route {i+1}").add_to(m)

        folium.Marker(start, icon=folium.Icon(color="green"), popup="Start").add_to(m)
        folium.Marker(end, icon=folium.Icon(color="red"), popup="End").add_to(m)

        return m.get_root().render()

    def get_route_coordinates(self, start, end):
        routes = self.get_routes(start, end)
        route_coords = []
        
        for r in routes:
            coords = []
            for node_id in r:
                node = self.G_simple.nodes[node_id]
                coords.append({
                    "lat": node["y"],
                    "lon": node["x"]
                })
            route_coords.append(coords)
            
        return route_coords

# -------------------------------
# MAIN (For Testing)
# -------------------------------
if __name__ == "__main__":
    engine = SafeRouteEngine()
    
    start = (
        float(input("Start latitude: ")),
        float(input("Start longitude: "))
    )
    end = (
        float(input("End latitude: ")),
        float(input("End longitude: "))
    )

    hanshal_routes(start, end)