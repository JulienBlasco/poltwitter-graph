class graphData():
    def __init__(self, graph):
        self.graph = graph

    def json_data(self):
        return {
            "nodes": [
                {
                    "id": node["id_str"],
                    "r": node["r"],
                    "g": node["g"],
                    "b": node["b"],
                    "label": node["name"],
                    "pagerank": node["pagerank_rt"],
                    "x": node["x"],
                    "y": -node["y"],
                    "size": node["size"],
                    "modularity_class": node["Modularity Class"]
                }
                for i, node in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": s,
                    "target": t,
                    "id": edge["Edge Id"],
                    "r": self.graph.node[s]["r"],
                    "g": self.graph.node[s]["g"],
                    "b": self.graph.node[s]["b"]
                }
                for s,t,edge in self.graph.edges(data=True)
            ]
        }