#!/usr/bin/env python

import os

from flask import Flask
from flask import render_template
from flask_reverse_proxy import FlaskReverseProxied
from flask.ext.assets import Bundle, Environment

from merge_view import show_fixture
from upload import upload, remove

app = Flask(__name__)

assets = Environment(app)
assets.load_path = [
    os.path.join(os.path.dirname(__file__), 'node_modules'),
    os.path.join(os.path.dirname(__file__), 'static')
]
main_js = Bundle(
    'angular/angular.min.js',
    'angular-sanitize/angular-sanitize.min.js')
main_css = Bundle(
    'bootstrap/dist/css/bootstrap.min.css')
viewer_js = Bundle(
    'angular-object-diff/dist/angular-object-diff.min.js',
    'app.js')
viewer_css = Bundle(
    'angular-object-diff/dist/angular-object-diff.css')
upload_js = Bundle('upload.js')

assets.register('main_js', main_js)
assets.register('main_css', main_css)
assets.register('viewer_js', viewer_js)
assets.register('viewer_css', viewer_css)
assets.register('upload_js', upload_js)

proxied = FlaskReverseProxied(app)

@app.route('/')
def index():
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    tests = [d for d in os.listdir(fixture_dir)]
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    try:
        uploads = [d for d in os.listdir(upload_dir)]
    except:
        uploads = []
    if app.config.get('READONLY'):
        readonly = True
        column_class = 'col-md-6'
    else:
        readonly= False
        column_class = 'col-md-4'
    return render_template('index.html',
                           tests=tests, uploads=uploads,
                           readonly=readonly, column_class=column_class)


app.route('/fixture/<dirname>/<fixture>')(show_fixture)


def get_app(config_dict):
    app.config.update(config_dict)
    if not app.config.get('READONLY'):
        app.route('/upload', methods=['POST'])(upload)
        app.route('/remove', methods=['POST'])(remove)


if __name__ == '__main__':
    app_inst = get_app({'SERVER_NAME': 'localhost:5000'})
    app.run(host='0.0.0.0', debug=True)
