#!/usr/bin/env python

import json
import os

from flask import Flask
from flask import render_template
from flask.ext.bower import Bower

from json_merger import UpdateMerger, MergeError
from json_merger.comparator import PrimaryKeyComparator
from json_merger.list_unify import UnifierOps


app = Flask(__name__)
Bower(app)

def _read_fixture(fixture, filename):
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures',
                               fixture)
    with open(os.path.join(fixture_dir, filename)) as f:
        return f.read()


class AuthorComparator(PrimaryKeyComparator):

    primary_key_fields = ['inspire_id']

    def equal(self, l1_idx, l2_idx):
        ret = super(AuthorComparator, self).equal(l1_idx, l2_idx)
        if not ret:
            return (self.l1[l1_idx]['full_name'][:5] ==
                    self.l2[l2_idx]['full_name'][:5])
        else:
            return True


class TitleComparator(PrimaryKeyComparator):

    primary_key_fields = ['source']


class AffiliationComparator(PrimaryKeyComparator):

    primary_key_fields = ['value']


COMPARATORS = {
    'authors': AuthorComparator,
    'authors.affiliations': AffiliationComparator,
    'titles': TitleComparator
}
LIST_MERGE_OPS = {
    'titles': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'authors.affiliations': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST
}


@app.route('/')
def index():
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    tests = [d for d in os.listdir(fixture_dir)
            if os.path.isdir(fixture_dir)]
    return render_template('index.html', tests=tests)


@app.route('/fixture/<fixture>')
def show_fixture(fixture):
    root = json.loads(_read_fixture(fixture, 'root.json'))
    head = json.loads(_read_fixture(fixture, 'head.json'))
    update = json.loads(_read_fixture(fixture, 'update.json'))
    description = _read_fixture(fixture, 'description.txt')
    # TODO call actual merge algorithm
    merger = UpdateMerger(root, head, update,
                          comparators=COMPARATORS,
                          list_merge_ops=LIST_MERGE_OPS)
    conflicts = None
    try:
        merger.merge()
    except MergeError as e:
        conflicts = e.content
    merged = merger.merged_root

    merge_info = {
            'root': root,
            'head': head,
            'update': update,
            'merged': merged,
            'conflicts': conflicts}

    return render_template('diff.html',
                           description=description,
                           merge_info=merge_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
