# Date: 11/04/2018
# Description: Main file

import os
from src.classifier import Classifier 
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, jsonify, redirect, url_for, flash

app = Flask(__name__)  
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.urandom(0x200) 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
PATH_TO_MODEL = 'ai/trained_models/cat_dog_1.h5' 

classifier = Classifier(PATH_TO_MODEL)


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload():        
    if 'file' not in request.files:
        flash('Upload an image')
        return redirect(url_for('index'))

    file = request.files['file']  

    if not file.filename:
        flash('No selected file')
        return redirect(url_for('index'))
 

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        prediction = classifier.predict(img_path)
        flash('I think it is a {}'.format(prediction))
        os.remove(img_path)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)