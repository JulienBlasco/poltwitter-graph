from flask import Blueprint

mod_proc_mining = Blueprint('process-mining', __name__, url_prefix='/process-mining', template_folder='templates',
                            static_folder='static')

from app.module_process_mining import model, controller, events