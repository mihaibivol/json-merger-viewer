from json_merger.comparator import PrimaryKeyComparator
from json_merger.list_unify import UnifierOps
from json_merger.contrib.inspirehep.author_util import (
    AuthorNameDistanceCalculator, NameToken, NameInitial)
from json_merger.contrib.inspirehep.comparators import (
    AuthorComparator as AuthorComparatorBase)

from inspirehep.modules.authors.utils import scan_author_string_for_phrases

def author_tokenize(name):
    phrases = scan_author_string_for_phrases(name)
    res = {'lastnames': [], 'nonlastnames': []}
    for key, tokens in phrases.items():
        lst = res.get(key)
        if lst is None:
            continue
        for token in tokens:
            if len(token) == 1:
                lst.append(NameInitial(token))
            else:
                lst.append(NameToken(token))
    return res


class AuthorComparator(AuthorComparatorBase):
    distance_function = AuthorNameDistanceCalculator(author_tokenize)


class SourceComparator(PrimaryKeyComparator):
    primary_key_fields = ['source']


class AffiliationComparator(PrimaryKeyComparator):
    primary_key_fields = ['value']


class CollectionsComparator(PrimaryKeyComparator):
    primary_key_fields = ['primary']


class ExtSysNumberComparator(PrimaryKeyComparator):
    primary_key_fields = ['institute']


COMPARATORS = {
    'authors': AuthorComparator,
    'authors.affiliations': AffiliationComparator,
    'titles': SourceComparator,
    'abstracts': SourceComparator,
    'collections': CollectionsComparator,
}
LIST_MERGE_OPS = {
    'titles': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'authors.affiliations': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'abstracts': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'collections': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
}
