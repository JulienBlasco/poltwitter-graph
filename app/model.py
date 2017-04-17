from collections import Counter
import operator

class graphData():
    def __init__(self, graph):
        self.graph = graph
        for node in self.graph.nodes():
            if self.graph.node[node]["Modularity Class"] == 17:
                self.graph.node[node]["r"] = 139
                self.graph.node[node]["g"] = 0
                self.graph.node[node]["b"] = 139

    def json_data(self):
        counts = Counter([(self.graph.node[n]["r"],
                           self.graph.node[n]["g"],
                           self.graph.node[n]["b"]) for n in self.graph.nodes()])
        sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
        class_to_cluster = {}
        for i in range(len(sorted_counts)):
            if i < 8:
                class_to_cluster[sorted_counts[i][0]] = i+1
            else:
                class_to_cluster[sorted_counts[i][0]] = 9

        return {
            "nodes": [
                {
                    "id": node["id_str"],
                    "r": node["r"],
                    "g": node["g"],
                    "b": node["b"],
                    "label": node["screen_name"],
                    "pagerank": node["pagerank_rt"],
                    "x": node["x"],
                    "y": -node["y"],
                    "size": node["size"],
                    "modularity_class": class_to_cluster[(node["r"], node["g"], node["b"])]
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