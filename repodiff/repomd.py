import pprint
from repodiff.diff_objects import RepomdDataDiff, MetadataDiff
from repodiff.package import Package
from repodiff.metadata import Metadata


class RepomdData(Package):

    DIFF_CLASS = RepomdDataDiff
    DIFF_ATTR = ('checksum_type',
                 'open_checksum_type')

    def __init__(self):
        Package.__init__(self)
        #self.name = ""
        #self.checksum = ""
        self.location_href = ""
        self.real_checksum = ""
        self.checksum_type = ""
        self.timestamp = ""
        self.size = ""
        self.open_size = ""
        self.open_checksum = ""
        self.open_checksum_type = ""
        self.database_version = ""


class RepomdDiff(MetadataDiff):
    def __init__(self, diff):
        MetadataDiff.__init__(self)
        if diff:
            self.__dict__.update(diff.__dict__)
        self.tags = None       # (1st_tags, 2nd_tags)
        self.revisions = None  # (1st_revision, 2nd_revision)

    def __nonzero__(self):
        if MetadataDiff.__nonzero__(self):
            return True
        return bool(self.tags) or bool(self.revisions)

    def pprint(self, chksum_to_name_dicts=None):
        msg = ""
        if self.revisions:
            msg += "  Different revisions:\n"
            msg += "    1. repomd:\n"
            msg += "      %s\n" % self.revisions[0]
            msg += "    2. repomd:\n"
            msg += "      %s\n" % self.revisions[1]
            msg += "    ----------------------------------------\n"
        if self.tags:
            msg += "  Different tags:\n"
            msg += "    1. repomd:\n"
            msg += pprint.pformat(self.tags[0], indent=6)
            msg += "\n    2. repomd:\n"
            msg += pprint.pformat(self.tags[1], indent=6)
            msg += "\n    ----------------------------------------\n"
        msg += MetadataDiff.pprint(self, chksum_to_name_dicts)
        return msg


class RepomdMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)
        self.tags = {}
        self.revision = ""

    def diff(self, other):
        diff = Metadata.diff(self, other)
        rdiff = RepomdDiff(diff)

        if not self.revision.isdigit() and not other.revision.isdigit():
            # Revision compare only if there are not numbers
            # Most of the time, revision is just a timestamp (number)
            # But in some cases (with --revision param) it could be any text
            if self.revision != other.revision:
                rdiff.revisions = (self.revision, other.revision)

        if self.tags != other.tags:
            rdiff.tags = (self.tags, other.tags)

        if rdiff:
            return rdiff
        return None

