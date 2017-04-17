#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, jsonify, render_template, send_from_directory, make_response, redirect, url_for
from app import model
import networkx as nx

app = Flask(__name__)

app.graph = model.graphData(nx.read_graphml("app/static/data/Big_component_enriched.graphml"))
app.data = app.graph.json_data()

@app.route("/")
def blank():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('static', 'favicon.ico')


@app.route("/data.json")
def data_json():
    return jsonify(app.data)


@app.route("/<page>")
@app.route("/<page>.html")
def specific_page(page):
    return render_template(page+".html")


@app.errorhandler(404)
def ma_page_404(error):
    return "Ma jolie page 404", 404
