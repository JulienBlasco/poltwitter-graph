#! /usr/bin/python
# -*- coding:utf-8 -*-

from PIL import Image
from io import BytesIO
from flask import Flask, render_template, make_response, redirect, url_for
from flask_socketio import SocketIO
from datetime import date

app = Flask(__name__)
socketio = SocketIO()
socketio.init_app(app)

@app.route("/")
def blank():
    return render_template("blank-page.html")

@app.route('/graphe')
def render_graph():
    return render_template("graphe.html")

@app.route('/<nom>')
def accueil(nom="visiteur"):
    d = date.today().isoformat()
    mots = ["bonjour", "à", "toi,", nom+"."]
    return render_template('index.html', titre="Bienvenue !", mots=mots, date=d)


@app.context_processor
def passer_ingredient():
    return dict(ingredient="caramel")


@app.route('/image')
def genere_image():
    mon_image = BytesIO()
    Image.new("RGB", (300,300), "#92C41D").save(mon_image, 'BMP')
    reponse = make_response(mon_image.getvalue(),404)
    reponse.mimetype = "image/bmp"
    return reponse
    #return redirect(url_for("accueil", nom="Jean-Michel"))


@app.errorhandler(404)
def ma_page_404(error):
    return "Ma jolie page 404", 404