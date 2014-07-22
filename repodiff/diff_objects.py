import difflib
import pprint
import pprint as libpprint

_MAX_LENGTH = 80

def pretty_diff(d1, d2):

    def safe_repr(obj, short=False):
        try:
            result = repr(obj)
        except Exception:
            result = object.__repr__(obj)
        if not short or len(result) < _MAX_LENGTH:
            return result
        return result[:_MAX_LENGTH] + ' [truncated]...'

    def sequence_diff(seq1, seq2, msg=None, seq_type=None):
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                return 'First sequence is not a %s: %s' % \
                        (seq_type_name, safe_repr(seq1))
            if not isinstance(seq2, seq_type):
                return 'Second sequence is not a %s: %s' % \
                        (seq_type_name, safe_repr(seq2))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        if differing is None:
            if seq1 == seq2:
                return

            seq1_repr = safe_repr(seq1)
            seq2_repr = safe_repr(seq2)
            if len(seq1_repr) > 30:
                seq1_repr = seq1_repr[:30] + '...'
            if len(seq2_repr) > 30:
                seq2_repr = seq2_repr[:30] + '...'
            elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
            differing = '%ss differ: %s != %s\n' % elements

            for i in xrange(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of first %s\n' %
                                 (i, seq_type_name))
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('\nUnable to index element %d of second %s\n' %
                                 (i, seq_type_name))
                    break

                if item1 != item2:
                    differing += ('\nFirst differing element %d:\n%s\n%s\n' %
                                 (i, item1, item2))
                    break
            else:
                if (len1 == len2 and seq_type is None and
                    type(seq1) != type(seq2)):
                    # The sequences are the same, but have differing types.
                    return

            if len1 > len2:
                differing += ('\nFirst %s contains %d additional '
                             'elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing += ('\nSecond %s contains %d additional '
                             'elements.\n' % (seq_type_name, len2 - len1))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))
        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))
        return standardMsg + '\n' + diffMsg

    def set_diff(set1, set2, msg=None):
        try:
            difference1 = set1.difference(set2)
        except TypeError, e:
            return 'invalid type when attempting set difference: %s' % e
        except AttributeError, e:
            return 'first argument does not support set difference: %s' % e

        try:
            difference2 = set2.difference(set1)
        except TypeError, e:
            return 'invalid type when attempting set difference: %s' % e
        except AttributeError, e:
            return 'second argument does not support set difference: %s' % e

        if not (difference1 or difference2):
            return

        lines = []
        if difference1:
            lines.append('Items in the first set but not the second:')
            for item in difference1:
                lines.append(repr(item))
        if difference2:
            lines.append('Items in the second set but not the first:')
            for item in difference2:
                lines.append(repr(item))

        return '\n'.join(lines)

    diff = None

    if not isinstance(d1, type(d2)):
        return diff
    if d1 == d2:
        return diff

    if isinstance(d1, dict):
        diff = ('\n' + '\n'.join(difflib.ndiff(
                pprint.pformat(d1).splitlines(),
                pprint.pformat(d2).splitlines())))
    elif isinstance(d1, list):
        diff = sequence_diff(d1, d2, seq_type=list)
    elif isinstance(d1, tuple):
        diff = sequence_diff(d1, d2, seq_type=tuple)
    elif isinstance(d1, set):
        diff = set_diff(d1, d2)
    elif isinstance(d1, frozenset):
        diff = set_diff(d1, d2)
    return diff


class PackageDiff(object):
    ITEM_NAME = "Package"

    def __init__(self):
        self.differences = []

    def __nonzero__(self):
        return bool(len(self.differences))

    def __repr__(self):
        return libpprint.pformat(self.__dict__)

    def add_difference(self, name, val_a, val_b, item_type=None, desc=None):
        self.differences.append((name, val_a, val_b, item_type, desc))

    def pprint(self):
        msg = ""
        for difference in self.differences:
            name, a, b, item_type, desc = difference

            msg += "     %s" % name
            if item_type:
                msg += " [%s]" % item_type
            if desc:
                msg += " - %s" % desc
            msg += "\n"

            nice_diff = pretty_diff(a, b)

            if isinstance(a, set):
                tmp_a = a - b
                b = b - a
                a = tmp_a
                msg += "    [The difference is set -> Only extra items are shown]\n"
            else:
                msg += "\n"
            msg += "      1. %s:\n" % self.ITEM_NAME
            msg += "        %s\n" % libpprint.pformat(a, indent=8)
            msg += "      2. %s:\n" % self.ITEM_NAME
            msg += "        %s\n" % libpprint.pformat(b, indent=8)
            if nice_diff:
                msg += "      Diff:\n"
                msg += "        %s\n" % "\n        ".join(nice_diff.split('\n'))

        return msg


class RepomdDataDiff(PackageDiff):
    ITEM_NAME = "Value"


class MetadataDiff(object):
    def __init__(self):
        self.missing_packages = set()  # set of checksums
        self.added_packages   = set()  # set of checksums
        self.changed_packages = set()  # set of checksums
        self.packages_diffs = {}
        # self.packges_diffs keys are values from self.changed_packages
        # and values are PackageDiff objects.

    def __nonzero__(self):
        return bool(len(self.missing_packages) or \
                    len(self.added_packages) or \
                    len(self.changed_packages))

    def __repr__(self):
        return libpprint.pformat(self.__dict__)

    def pprint(self, chksum_to_name_dicts=None):
        def translate(chksum):
            if not chksum_to_name_dicts:
                return chksum
            for chk_dict in chksum_to_name_dicts:
                if chksum in chk_dict:
                    return chk_dict[chksum]
            return chksum

        msg = ""
        if self.missing_packages:
            msg += "  Missing packages:\n"
            for pkg in self.missing_packages:
                msg += "    %s\n" % translate(pkg)
        if self.added_packages:
            msg += "  Added packages:\n"
            for pkg in self.added_packages:
                msg += "    %s\n" % translate(pkg)
        if self.changed_packages:
            msg += "  Changed packages:\n"
            for pkg in self.changed_packages:
                msg += "    %s\n" % translate(pkg)
                msg += self.packages_diffs[pkg].pprint()
                msg += "    ----------------------------------------\n"
        return msg


class OneRepoDiff(object):
    def __init__(self, chksum_to_name_dicts=None):
        self.chksum_to_name_dicts = chksum_to_name_dicts
        self.pri_diff = None
        self.fil_diff = None
        self.oth_diff = None

    def __nonzero__(self):
        return bool(self.pri_diff or self.fil_diff or self.oth_diff)

    def __repr__(self):
        return libpprint.pformat(self.__dict__)

    def pprint(self):
        msg = ""
        if self.pri_diff:
            msg += "PRIMARY repodata are different:\n"
            msg += self.pri_diff.pprint(chksum_to_name_dicts=self.chksum_to_name_dicts)
        if self.fil_diff:
            msg += "FILELISTS repodata are different:\n"
            msg += self.fil_diff.pprint(chksum_to_name_dicts=self.chksum_to_name_dicts)
        if self.oth_diff:
            msg += "OTHER repodata are different:\n"
            msg += self.oth_diff.pprint(chksum_to_name_dicts=self.chksum_to_name_dicts)
        return msg


class CompleteRepoDiff(object):
    def __init__(self):
        self.xml_repo_diff = None
        self.sql_repo_diff = None
        self.md_diff       = None

    def __nonzero__(self):
        return bool(self.xml_repo_diff or self.sql_repo_diff or self.md_diff)

    def __repr__(self):
        return libpprint.pformat(self.__dict__)

    def pprint(self):
        msg = ""
        if self.xml_repo_diff:
            msg += "=== XML REPO DIFF: ===\n"
            msg += self.xml_repo_diff.pprint()
        if self.sql_repo_diff:
            msg += "=== SQLITE REPO DIFF: ===\n"
            msg += self.sql_repo_diff.pprint()
        if self.md_diff:
            msg += "=== REPOMD.XML DIFF: ===\n"
            msg += self.md_diff.pprint()
        return msg
