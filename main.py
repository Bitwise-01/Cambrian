# Date: 11/04/2018
# Description: Main file

from flask import Flask, render_template, request, session, jsonify, redirect, url_for

app = Flask(__name__)  

@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)