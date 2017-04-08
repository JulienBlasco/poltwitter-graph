from flask import Flask, redirect
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# to make flask less verbose
# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

# App, socketio and SQLAlchemy db definition
app = Flask(__name__)
socketio = SocketIO()

app.config.from_object('app.config')
db = SQLAlchemy(app)

# user_datastore definition
from flask_security import SQLAlchemyUserDatastore
from app.module_security.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# App creation function, will be used in process-mining.py
def create_app(appli):
    from app.module_process_mining import model
    # General configuration
    appli.config.from_object('app.config')  # General Configuration

    # Security module launching
    from flask_security import Security
    appli.config['SECURITY_URL_PREFIX'] = '/security'
    appli.config['SECURITY_POST_LOGIN_VIEW'] = 'process-mining/'
    appli.config['SECURITY_UNAUTHORIZED_VIEW'] = None
    Security(appli, user_datastore, register_blueprint=True)

    # Process Mining module launching
    from app.module_process_mining import mod_proc_mining
    appli.register_blueprint(mod_proc_mining)

    # SQLAlchemy initialization
    db.init_app(appli)

    # Socketio initialization
    socketio.init_app(appli)

    model.PandasProcessModel.set_process_data(pd.read_csv("data/event_log.csv"))

    return appli


@app.route('/')
def index():
    return redirect('/security/login', code=302)
