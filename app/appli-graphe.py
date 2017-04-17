import flask_app
#from app import socketio

if __name__ == '__main__':
    #socketio.run(app)
    flask_app.app.run(debug=True)