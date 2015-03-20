import os
import sys

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'venv', 'Lib', 'site-packages'))

from google.appengine.ext import blobstore
from werkzeug.http import parse_options_header
from flask import Flask, request, jsonify, render_template, abort, make_response
from flask.ext.cors import CORS, cross_origin

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_url_path='')
# cors = CORS(app, resources={r'/api/*': {"origins": "*"}}, allow_headers='Content-Type')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/")
@cross_origin()
def hello():
    uploadUri = blobstore.create_upload_url('/uploads')
    return jsonify(uploadUri=uploadUri)


@app.route("/uploads", methods=['POST'])
@cross_origin()
def upload_image():
    file = request.files['file']
    if file and allowed_file(file.filename):
        header = file.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        return jsonify(filename=blob_key)
    else:
        abort(400)
        # return redirect(url_for('uploaded_file', filename=filename))


@app.route("/api/uploads/<filename>")
@cross_origin()
def uploaded_file(filename):
    blob_info = blobstore.get(filename)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
