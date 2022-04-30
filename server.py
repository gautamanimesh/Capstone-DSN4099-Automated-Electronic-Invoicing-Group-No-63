import os
import config
from flask import Flask, request, render_template, send_file, flash
from werkzeug.utils import secure_filename
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = (secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename)
        config.filename = filename
        flash("Your file has been successfully uploaded", "info")
        return render_template('index.html')


@app.route('/download')
def download_file():
    filename = config.finalfile
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()

