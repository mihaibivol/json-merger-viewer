import json
import os
import re
import requests
import shutil

from StringIO import StringIO

from flask import redirect, request, url_for
from dojson.contrib.marc21.utils import create_record
from inspirehep.modules.migrator.tasks.records import split_stream
from inspirehep.dojson.processors import overdo_marc_dict
from inspirehep.factory import create_app


def _get_file(fp, file_type):
    if file_type == 'json':
        return json.load(fp)
    elif file_type == 'xml':
        inspire_app = create_app()
        with inspire_app.app_context():
            rec = overdo_marc_dict(create_record(split_stream(fp).next()))
        return rec
    else:
        return {}


def _get_json(field):
    url_field = field + 'URL'
    if url_field in request.form:
        if request.form[url_field].startswith('/'):
            with open(request.form[url_field]) as f:
                return _get_file(f, request.form[url_field].split('.')[-1])
        rsp = requests.get(request.form[url_field])
        if 'json' in rsp.headers.get('Content-Type', '').lower():
            return _get_file(StringIO(rsp.content), 'json')
        elif 'xml' in rsp.headers.get('Content-Type', '').lower():
            return _get_file(StringIO(rsp.content), 'xml')
        else:
            return {}
    elif field in request.files:
        obj_file = request.files[field]
        if obj_file.filename.endswith('json'):
            return _get_file(obj_file, 'json')
        elif obj_file.filename.endswith('xml'):
            return _get_file(obj_file, 'xml')
        else:
            return {}
    else:
        return {}

def upload():
    test_name = request.form['testname']
    if not re.match(r'^[a-zA-Z0-9_]+$', test_name):
        return 'Please provide a good test name'
    test_path = os.path.join(os.path.dirname(__file__), 'uploads', test_name)
    while os.path.exists(test_path):
        test_path += '_copy'
    try:
        root = _get_json('root')
        update = _get_json('update')
        if not update:
            return 'Update object is empty or none'
        head = _get_json('head')
        if not head:
            return 'Head object is empty or none'
    except Exception as e:
        raise
        return 'Error when deserializing {}'.format(e)
    description = 'Uploaded file.'
    os.makedirs(test_path)
    with open(os.path.join(test_path, 'root.json'), 'w') as f:
        json.dump(root, f)
    with open(os.path.join(test_path, 'head.json'), 'w') as f:
        json.dump(head, f)
    with open(os.path.join(test_path, 'update.json'), 'w') as f:
        json.dump(update, f)
    with open(os.path.join(test_path, 'description.txt'), 'w') as f:
        f.write(description)
    return redirect(url_for('index'))


def remove():
    test_name = request.form['test']
    path = os.path.join(os.path.dirname(__file__), 'uploads', test_name)
    shutil.rmtree(path)
    return redirect(url_for('index'))
