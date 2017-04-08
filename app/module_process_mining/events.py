import io
from datetime import datetime
from time import time

from flask import session

import pandas as pd
from flask_socketio import emit

from app.module_process_mining import model
from app import socketio


def data():
    datatable_csv = """case_id,event,timestamp,user
1111,written,15/07/2016,marchand
1111,sent,16/07/2016,marchand
1111,received,17/07/2016,rioust
2222,written,18/07/2016,blasco
2222,sent,19/07/2016,blasco
2222,received,20/07/2016,burel
2222,forwarded,21/07/2016,burel
2222,received,22/07/2016,rioust
3333,written,23/07/2016,blasco
3333,deleted,24/07/2016,blasco
4444,written,25/07/2016,rioust
4444,sent,26/07/2016,rioust
4444,received,27/07/2016,marchand
4444,received,28/07/2016,burel
4444,received,29/07/2016,blasco"""
    return pd.read_csv(io.StringIO(datatable_csv), delimiter=',')


@socketio.on("connect", namespace="/test")
def initialize():
    session['processModel'] = model.PandasProcessModel("Event Log")
    emit("highchartsData", session['processModel'].message_to_send())


@socketio.on('addFilter', namespace='/test')
def add_filter(message):
    t = time()
    if message["filterType"] == 'list':
        filter_to_add = model.PandasListFilter(message["filterBy"], message["filterList"])
    elif message["filterType"] == "daily":
        range_from = message["date"]/1000.0
        range_to = range_from + 3600*24
        filter_to_add = model.PandasRangeFilter('timestamp',
                                                datetime.fromtimestamp(range_from),
                                                datetime.fromtimestamp(range_to))
    elif message["filterType"] == "timeRange":
        range_from = message["lower"] / 1000.0
        range_to = message["upper"] / 1000.0
        filter_to_add = model.PandasRangeFilter('timestamp',
                                                datetime.fromtimestamp(range_from),
                                                datetime.fromtimestamp(range_to))
    elif message["filterType"] == "link":
        node_from = message['nodeFrom']
        node_to = message['nodeTo']
        filter_to_add = model.PandasLinkFilter(node_from, node_to)

    session['processModel'].add_filter(filter_to_add)
    emit("highchartsData", session['processModel'].message_to_send())

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "addFilter of type", message["filterType"], "triggered:", filter_to_add,
          "-- data sent in", '%.3f' % (time()-t), "seconds.")
    # TODO Update datatable.js data
    # TODO Resend datatables.js data


@socketio.on('removeFilter', namespace='/test')
def remove_filter(message):
    t = time()
    session['processModel'].remove_filter(message["filterIdx"])
    emit("highchartsData", session['processModel'].message_to_send())
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "removeFilter of id", message["filterIdx"],
          "-- data sent in", '%.3f' % (time() - t), "seconds.")
    # TODO Optional: Update datatable.js data
    # TODO Resend datatables.js data