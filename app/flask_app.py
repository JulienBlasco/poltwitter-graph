#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, jsonify, render_template, send_from_directory, make_response, redirect, url_for
import model
import networkx as nx

app = Flask(__name__)

index_to_path = {
    "1": "../output/Big_component_enriched.graphml",
    "2": "../output/Big_component_reduced.graphml"
}

app.graph = {
    i: model.graphData(nx.read_graphml(index_to_path[i])) for i in index_to_path
}

app.data = {
    i: graph.json_data() for i, graph in app.graph.items()
}


app.graph_index = "1"


app.wordcloud = {
    str(c): app.graph[app.graph_index].json_words(
        nodes=app.data[app.graph_index]["graph"]["nodes"],
        cluster=c) for c in range(1, 10)
}

@app.route("/")
def graph():
    return render_template("home.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('static', 'favicon.ico')


@app.route("/data_<i>.json")
def data_json(i):
    return jsonify(app.data[i]["graph"])

@app.route("/names_data_<i>.json")
def names_data_json(i):
    return jsonify(app.data[i]["names"])


@app.route("/graph=<i>")
def choose_graph(i):
    app.graph_index = i
    return redirect("graph")

@app.route("/<page>")
@app.route("/<page>.html")
def specific_page(page):
    return render_template(page+".html",
                           graph_index=app.graph_index,
                           graph_names=app.data[app.graph_index]["names"])


@app.route("/barchart_data_<cluster>")
def barchart_data_json(cluster):
    return jsonify(model.json_barchart(app.data[app.graph_index]["graph"]["nodes"], cluster=cluster))


@app.route("/wordcloud_data_<cluster>")
def wordcloud_data_json(cluster):
    if app.graph_index == "2":
        return jsonify([{
            "text": "nuage non pertinent pour le petit graphe",
            "weight": 1}])
    else:
        return jsonify(app.wordcloud[cluster])


@app.route("/statistics_<cluster>")
def statistics(cluster):
    return jsonify(app.graph[app.graph_index].get_statistics(app.data[app.graph_index]["graph"]["nodes"],
                                                             cluster=cluster))


@app.errorhandler(404)
def ma_page_404(error):
    return "Ma jolie page 404", 404
