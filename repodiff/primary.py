from repodiff.package import Package
from repodiff.metadata import Metadata


class PrimaryPackage(Package):

    DIFF_ATTR = None

    def __init__(self):
        Package.__init__(self)
        self.pkgkey = ""
        #self.checksum = ""
        #self.name = ""
        #self.epoch = ""
        #self.version = ""
        #self.release = ""
        #self.arch = ""
        self.summary = ""
        self.description = ""
        self.url = ""
        self.time_file = ""
        self.time_build = ""
        self.license = ""
        self.vendor = ""
        self.group = ""
        self.buildhost = ""
        self.sourcerpm = ""
        self.header_start = ""
        self.header_end = ""
        self.packager = ""
        self.size_package = ""
        self.size_installed = ""
        self.size_archive = ""
        self.location = ""
        self.location_base = ""
        self.checksum_type = ""
        self.provides = set([])  # set([('fn', flags, epoch, ver, rel), ...])
        self.conflicts = set([])  # -||-
        self.obsoletes = set([])  # -||-
        self.requires = set([]) # set([(fn, flags, epoch, ver, rel, pre), ...])
        # ^^^ It's because there can be multiple files with the
        #     same name, but different attributes
        self.files = set()  # primary_files
        self.dirs = set()  # primary_dirs
        self.ghosts = set()  # primary_ghosts

        # Let's diff all of out attributes
        if not self.DIFF_ATTR:
            self.DIFF_ATTR = self.__dict__.keys()


class PrimaryMetadata(Metadata):

    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)

    def checksum_to_name(self, checksum):
        if checksum in self:
            return self.items[checksum].nevra()
        return None
