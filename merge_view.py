import copy
import json

import os

from flask import request, render_template

from json_merger.merger import Merger
from json_merger.utils import get_obj_at_key_path
from json_merger.config import DictMergerOps, UnifierOps
from json_merger.errors import MergeError

from merger_config import COMPARATORS, LIST_MERGE_OPS

def _read_fixture(dirname, fixture, filename):
    fixture_dir = os.path.join(os.path.dirname(__file__), dirname,
                               fixture)
    with open(os.path.join(fixture_dir, filename)) as f:
        return f.read()



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


def show_fixture(dirname, fixture):
    root = json.loads(_read_fixture(dirname, fixture, 'root.json'))
    head = json.loads(_read_fixture(dirname, fixture, 'head.json'))
    update = json.loads(_read_fixture(dirname, fixture, 'update.json'))
    description = _read_fixture(dirname, fixture, 'description.txt')
    listop = request.args.get('listop', UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    dictop = request.args.get('dictop', DictMergerOps.FALLBACK_KEEP_HEAD)
    merger = Merger(root, head, update,
                    dictop, listop,
                    comparators=COMPARATORS,
                    list_merge_ops=LIST_MERGE_OPS)
    conflicts = None
    try:
        merger.merge()
    except MergeError as e:
        conflicts = [json.loads(c.to_json()) for c in e.content]
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
            'head': head,
            'update': update,
            'rhRoot': rh_root,
            'rhHead': rh_head,
            'ruRoot': ru_root,
            'ruUpdate': ru_update,
            'hmMerged': hm_merged,
            'hmHead': hm_head,
            'conflicts': conflicts}

    # Some weird introspection
    dictops = [d for d in DictMergerOps.__dict__ if not d.startswith('_') and 'allowed' not in d.lower()]
    listops = [l for l in UnifierOps.__dict__ if not l.startswith('_') and 'allowed' not in l.lower()]
    return render_template('diff.html',
                           description=description,
                           listops=listops,
                           dictops=dictops,
                           dictop=dictop,
                           listop=listop,
                           merge_info=merge_info)
