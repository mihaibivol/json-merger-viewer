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


def put_id(obj, uid):
    try:
        obj['_id'] = uid
    except:
        pass


def build_root_diff(root, revision, stats):
    root = copy.deepcopy(root)
    revision = copy.deepcopy(revision)
    for key_path, stat in stats.items():
        next_uid = -1
        root_list = get_obj_at_key_path(root, key_path)
        if root_list is None:
            continue
        rev_list = get_obj_at_key_path(revision, key_path)
        if rev_list is None:
            continue

        for root_idx, root_obj in enumerate(root_list):
            if root_idx in stat.root_root_match_uids:
                put_id(root_obj, stat.root_root_match_uids[root_idx])
            else:
                put_id(root_obj, next_uid)
                next_uid -= 1

        for rev_idx, rev_obj in enumerate(rev_list):
            if rev_idx in stat.lst_root_match_uids:
                put_id(rev_obj, stat.lst_root_match_uids[rev_idx])
            else:
                put_id(rev_obj, next_uid)
                next_uid -= 1

    return root, revision


def build_merged_diff(merged, merged_uids, revision, stats):
    merged = copy.deepcopy(merged)
    revision = copy.deepcopy(revision)
    for key_path, uids in merged_uids.items():
        merged_list = get_obj_at_key_path(merged, key_path)
        if merged_list is None:
            continue
        for idx, uid in enumerate(uids):
            try:
                merged_list[idx]['_id'] = uid
            except:
                pass

    for key_path, stat in stats.items():
        rev_list = get_obj_at_key_path(revision, key_path)
        next_uid = -1
        if rev_list is None:
            continue
        for rev_idx, rev_obj in enumerate(rev_list):
            if rev_idx in stat.match_uids:
                put_id(rev_obj, stat.match_uids[rev_idx])
            else:
                put_id(rev_obj, next_uid)
                next_uid -= 1

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

    r_h_root, r_h_head = build_root_diff(root, head, merger.head_stats)
    r_u_root, r_u_updt = build_root_diff(root, update, merger.update_stats)
    h_m_merged, h_m_head = build_merged_diff(merged, merger.match_uids,
                                             head, merger.head_stats)

    merge_info = {
            'r_h_root': r_h_root,
            'r_h_head': r_h_head,
            'r_u_root': r_u_root,
            'r_u_update': r_u_updt,
            'h_m_merged': h_m_merged,
            'h_m_head': h_m_head,
            'conflicts': conflicts}

    return render_template('diff.html',
                           description=description,
                           merge_info=merge_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
