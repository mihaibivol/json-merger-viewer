#!/usr/bin/env python

import copy
import json
import os

from flask import Flask
from flask import render_template
from flask.ext.bower import Bower

from json_merger import UpdateMerger, MergeError
from json_merger.comparator import PrimaryKeyComparator
from json_merger.list_unify import UnifierOps
from json_merger.utils import get_obj_at_key_path


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


def build_root_diff(root, revision, stats):
    root = copy.deepcopy(root)
    revision = copy.deepcopy(revision)
    for key_path, stat in sorted(stats.items(), key=lambda x: len(x[0])):
        root_l = get_obj_at_key_path(root, key_path)
        if root_l is None:
            continue
        rev_l = get_obj_at_key_path(revision, key_path)
        if rev_l is None:
            continue
        for rev_obj, root_obj in stat.not_in_result_root_match_pairs:
            root_l.append(root_obj)
            rev_l.append(rev_obj)
        for rev_obj in stat.not_in_result_not_root_match:
            root_l.append('The RHS elem will not be in the end result')
            rev_l.append(rev_obj)
        for root_obj in stat.not_matched_root_objects:
            root_l.append(root_obj)

    return root, revision


def build_merged_diff(merged, revision, stats):
    merged = copy.deepcopy(merged)
    revision = copy.deepcopy(revision)
    for key_path, stat in sorted(stats.items(), key=lambda x: len(x[0])):
        rev_l = get_obj_at_key_path(revision, key_path)
        if rev_l is None:
            continue
        for rev_obj in stat.not_in_result:
            rev_l.append(rev_obj)
    return merged, revision


@app.route('/fixture/<fixture>')
def show_fixture(fixture):
    root = json.loads(_read_fixture(fixture, 'root.json'))
    head = json.loads(_read_fixture(fixture, 'head.json'))
    update = json.loads(_read_fixture(fixture, 'update.json'))
    description = _read_fixture(fixture, 'description.txt')
    merger = UpdateMerger(root, head, update,
                          comparators=COMPARATORS,
                          list_merge_ops=LIST_MERGE_OPS)
    conflicts = None
    try:
        merger.merge()
    except MergeError as e:
        conflicts = e.content
    merged = merger.merged_root

    rh_root, rh_head = build_root_diff(merger.aligned_root,
                                       merger.aligned_head,
                                       merger.head_stats)
    ru_root, ru_update = build_root_diff(merger.aligned_root,
                                         merger.aligned_update,
                                         merger.update_stats)
    hm_merged, hm_head = build_merged_diff(merged, merger.aligned_head,
                                           merger.head_stats)

    merge_info = {
            'root': root,
            'rhRoot': rh_root,
            'rhHead': rh_head,
            'ruRoot': ru_root,
            'ruUpdate': ru_update,
            'hmMerged': hm_merged,
            'hmHead': hm_head,
            'conflicts': conflicts}

    return render_template('diff.html',
                           description=description,
                           merge_info=merge_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
