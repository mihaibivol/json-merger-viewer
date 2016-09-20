from json_merger.comparator import PrimaryKeyComparator
from json_merger.list_unify import UnifierOps
from json_merger.contrib.inspirehep.author_util import (
    AuthorNameDistanceCalculator, AuthorNameNormalizer, NameToken, NameInitial)
from json_merger.contrib.inspirehep.comparators import (
        DistanceFunctionComparator)

from inspirehep.modules.authors.utils import scan_author_string_for_phrases

def author_tokenize(name):
    """This is how the name should be tokenized for the matcher."""
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


class NewIDNormalizer(object):
    """Callable that can be used to normalize by a given id for authors.
    Because now all the ids are in the list."""
    def __init__(self, id_type):
        self.id_type = id_type

    def __call__(self, author):
        """Sadly this will get only the first one. but well, it's just an
        optimisation for faster matches."""

        for id_field in author.get('ids', []):
            if id_field.get('type').lower() == self.id_type.lower():
                return id_field.get('value')
        # This is safe since the normalization is not the final decider.
        return None


class AuthorComparator(DistanceFunctionComparator):
    threhsold = 0.12
    distance_function = AuthorNameDistanceCalculator(author_tokenize)
    norm_functions = [
            NewIDNormalizer('ORCID'),
            NewIDNormalizer('INSPIRE BAI'),
            AuthorNameNormalizer(author_tokenize),
            AuthorNameNormalizer(author_tokenize, 1),
            AuthorNameNormalizer(author_tokenize, 1, True)
    ]


def get_pk_comparator(primary_key_fields, normalization_functions=None):
    class Ret(PrimaryKeyComparator):
        pass
    Ret.primary_key_fields = primary_key_fields
    Ret.normalization_functions = normalization_functions or {}
    return Ret


SourceComparator = get_pk_comparator(['source'])
AffiliationComparator = get_pk_comparator(['value'])
CollectionsComparator = get_pk_comparator(['primary'])
ExtSysNumberComparator = get_pk_comparator(['institute'])
URLComparator = get_pk_comparator(['url'])
PubInfoComparator = get_pk_comparator([
    ['journal_title', 'journal_volume', 'page_start'],
    ['journal_title', 'journal_volume', 'artid']])



COMPARATORS = {
    'authors': AuthorComparator,
    'authors.affiliations': AffiliationComparator,
    'abstracts': SourceComparator,
    'collections': CollectionsComparator,
    'external_system_numbers': ExtSysNumberComparator,
    'publication_info': PubInfoComparator,
}

# We an always default to KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST so
# this is less verbose.
LIST_MERGE_OPS = {
    'titles': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'authors.affiliations': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'abstracts': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'collections': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'external_system_numbers': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'publication_info': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'subject_terms': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'urls': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
    'public_notes': UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST,
}
