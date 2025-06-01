from config import config
import networkx as nx

class TrafficUtils:

    @staticmethod
    def calculate_center_limits():
        center = config["SIMULATION_CENTER"]
        road_half = config["ROAD_WIDTH"] // 2
        limits = {
            "top": center[1] - road_half,
            "bottom": center[1] + road_half,
            "left": center[0] - road_half,
            "right": center[0] + road_half
        }
        return limits

    @staticmethod
    def pedestrian_graph():
        weight = config["ROAD_WIDTH"]
        edges = [
            ("TL", "SW", {"weight": weight, "direction": "N"}),
            ("TL", "TR", {"weight": weight, "direction": "E"}),
            ("TL", "BL", {"weight": weight, "direction": "S"}),
            ("TL", "EN", {"weight": weight, "direction": "W"}),
            ("TR", "SE", {"weight": weight, "direction": "N"}),
            ("TR", "WN", {"weight": weight, "direction": "E"}),
            ("TR", "BR", {"weight": weight, "direction": "S"}),
            ("TR", "TL", {"weight": weight, "direction": "W"}),
            ("BR", "TR", {"weight": weight, "direction": "N"}),
            ("BR", "WS", {"weight": weight, "direction": "E"}),
            ("BR", "NE", {"weight": weight, "direction": "S"}),
            ("BR", "BL", {"weight": weight, "direction": "W"}),
            ("BL", "TL", {"weight": weight, "direction": "N"}),
            ("BL", "BR", {"weight": weight, "direction": "E"}),
            ("BL", "NW", {"weight": weight, "direction": "S"}),
            ("BL", "ES", {"weight": weight, "direction": "W"}),
            ("EN", "TL", {"weight": weight, "direction": "E"}),
            ("SW", "TL", {"weight": weight, "direction": "S"}),
            ("SE", "TR", {"weight": weight, "direction": "S"}),
            ("WN", "TR", {"weight": weight, "direction": "W"}),
            ("WS", "BR", {"weight": weight, "direction": "W"}),
            ("NE", "BR", {"weight": weight, "direction": "N"}),
            ("NW", "BL", {"weight": weight, "direction": "N"}),
            ("ES", "BL", {"weight": weight, "direction": "E"}),
        ]

        graph = nx.DiGraph()
        graph.add_edges_from(edges)

        return graph