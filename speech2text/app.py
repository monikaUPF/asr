import os
import tempfile
import socket

from werkzeug.utils import secure_filename
from flask import Flask, request, flash, redirect, url_for

import transcriber as tr

ALLOWED_EXTENSIONS = ['wav']


app = Flask(__name__)

transcriber = None


@app.route("/")
def hello():
    html = "<h3>Hello!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>"

    return html.format(hostname=socket.gethostname())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/speech2text", methods=['GET', 'POST'])
def speech2text():
    global transcriber

    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):

            with tempfile.NamedTemporaryFile() as fd:
                file.save(fd)
                result = transcriber.predict(fd.name)

            return result

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__":
    cfg_path = "/ASR/conf/decode.cfg"
    transcriber = tr.Transcriber(cfg_path)

    app.run(host='0.0.0.0', port=80)

