import pprint

from repodiff.metadata import MetadataItem
from repodiff.diff_objects import PackageDiff


class Package(MetadataItem):

    DIFF_CLASS = PackageDiff
    DIFF_ATTR = ('checksum')
    NONE_AND_EMPTY_ARE_SAME = ("location_base",
                               "vendor",
                               "description",
                               "sourcerpm")

    def __init__(self):
        MetadataItem.__init__(self)
        self.checksum = ''  # pkgid
        self.epoch = ''
        self.name = ''
        self.version = ''
        self.release = ''
        self.arch = ''

    def __repr__(self):
        str_repr = self.checksum
        if self.nevra():
            str_repr += "-%s" % self.nevra()
        return str_repr

    def nevra(self):
        nevra = self.name
        if self.version:
            nevra += "-"
            if self.epoch and self.epoch != "0":
                nevra += self.epoch + ":"
            nevra += self.version
            nevra += "-" + self.release
        if self.arch:
            nevra += "." + self.arch
        return nevra

    def pprint(self):
        msg = "%s (%s)\n" % (self.nevra(), self.checksum)
        print msg
