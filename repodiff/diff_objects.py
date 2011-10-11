import pprint as libpprint

class PackageDiff(object):
    def __init__(self):
        self.changed_attributes = set()  # Set of changed attributes
        self.attr_values = {}
        # attr_values look like:
        # {'attr_name': (first_pkg_attr_val, second_pkg_attr_val), ...}
        # keys are values from self.changed_attributes

    def __nonzero__(self):
        return bool(len(self.changed_attributes))

    def __repr__(self):
        return libpprint.pformat(self.__dict__)

    def pprint(self):
        msg = ""
        for attr in self.changed_attributes:
            msg += "    Attribute: %s" % attr
            a = self.attr_values[attr][0]
            b = self.attr_values[attr][1]
            if isinstance(a, set):
                tmp_a = a - b
                b = b - a
                a = tmp_a
                msg += " (Attribute is set -> Show only difference)\n"
            else:
                msg += "\n"
            msg += "      1. Package:\n"
            msg += "        %s\n" % libpprint.pformat(a, indent=2)
            msg += "      2. Package:\n"
            msg += "        %s\n" % libpprint.pformat(b, indent=2)
        return msg


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

    def __nonzero__(self):
        return bool(self.xml_repo_diff or self.sql_repo_diff)

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
        return msg
