#! /usr/bin/python
# -*- coding:utf-8 -*-

from io import BytesIO
from flask import Flask, render_template, make_response, redirect, url_for
# from flask_socketio import SocketIO
from datetime import date

app = Flask(__name__)
# socketio = SocketIO()
# socketio.init_app(app)


@app.route("/")
def blank():
    return render_template("index.html")


@app.route("/<page>")
@app.route("/<page>.html")
def specific_page(page):
    return render_template(page+".html")


@app.errorhandler(404)
def ma_page_404(error):
    return "Ma jolie page 404", 404