import os
import imghdr
from flask import render_template, redirect, flash, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from app import app

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            return "Invalid image",400
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], 'temp.jpg'))
    return '',204

@app.route('/uploads/')
def upload():
    return send_from_directory("../" + app.config['UPLOAD_PATH'], 'temp.jpg')

@app.route('/uploads/flip/')
def flip():
    org_img = Image.open(app.config['UPLOAD_PATH']+ "/" + 'temp.jpg')
    new_img = org_img.transpose(method=Image.FLIP_LEFT_RIGHT)
    new_img.save(app.config['UPLOAD_PATH'] + "/" + 'temp.jpg')
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413