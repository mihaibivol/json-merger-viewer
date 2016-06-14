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
