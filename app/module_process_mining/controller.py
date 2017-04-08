from flask import render_template

from app.module_process_mining import mod_proc_mining

@mod_proc_mining.route('/upload', methods=['POST', 'GET'])
#@login_required
def upload():
    # TODO add upload.html file
    return render_template('upload.html')


@mod_proc_mining.route('/', methods=['POST', 'GET'])
#@login_required
def process_mining_main():
    return render_template('process-mining.html')