from collections import Counter
import operator
import os
import json

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

        graph_data = {
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

        graph_noms_des_clusters = [
            (i+1, "checkCluster"+str(i+1), node[0]) for i, node in
                enumerate([
                sorted({
                    n["label"]: n["pagerank"]
                    for n in graph_data["nodes"] if n["modularity_class"] == i+1
                       }.items(), key=operator.itemgetter(1), reverse=True)[0]
                for i in range(9)
            ])
        ]

        return {
            "graph": graph_data,
            "names": graph_noms_des_clusters
        }

    def json_words(self, nodes, cluster=1, top=20):
        # ids = [
        #     n["id"] for n in nodes if n["modularity_class"] == int(cluster)
        # ]
        # hashtags = []
        # hashtag_counts = Counter(hashtags)
        # print(len(ids))
        # for id in ids:
        #     with open("../data/11 - topolitiq_2017-03-23_friends_tweets/" + id + ".tweets") as tweet_file:
        #         user_tweets = json.load(tweet_file)
        #         user_hashtags = [
        #             h["text"].lower() for t in user_tweets for h in t["entities"]["hashtags"]
        #         ]
        #         hashtag_counts.update(user_hashtags)
        # sorted_hashtags = sorted(hashtag_counts.items(),
        #                          key=operator.itemgetter(1),
        #                          reverse=True)[:(100 if len(hashtag_counts)>100 else len(hashtag_counts))]
        # print("Finished wordcloud " + str(cluster))
        # with open("../data/json_words_" + str(cluster) + ".json", "w") as file:
        #     json.dump( [
        #         {
        #             "text": hashtag[0],
        #             "weight": hashtag[1]
        #         }
        #         for hashtag in sorted_hashtags
        # ], file)
        with open("../data/json_words_" + str(cluster) + ".json") as file:
            return json.load(file)[:top]


def json_barchart(nodes, criterium="pagerank", top=5, cluster=1):
    top_accounts = sorted(
        [
            n for n in nodes
            if n["modularity_class"] == int(cluster)
        ],
        key=lambda n: n[criterium],
        reverse=True
    )[:top]

    node = top_accounts[0]
    return {
        "labels": [n["label"] for n in top_accounts],
        "datasets": [
            {
                "label": criterium,
                "backgroundColor": 'rgba(' + ",".join([
                    str(c) for c in [node["r"], node["g"], node["b"]]
                ]) + ',0.2)',
                "borderColor": 'rgba(' + ",".join([
                    str(c) for c in [node["r"], node["g"], node["b"]]
                ]) + ',1)',
                "borderWidth": 1,
                "data": [
                    100 * n[criterium] / node[criterium] for n in top_accounts
                ]
            }
        ]
    }