from repodiff.package import Package
from repodiff.metadata import Metadata


class PrimaryPackage(Package):

    DIFF_ATTR = None

    def __init__(self):
        Package.__init__(self)
        self.pkgkey = ""
        self.arch = ""
        self.version = ""
        self.epoch = ""
        self.release = ""
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
        self.provides  = {}  # {'filename': (flags, epoch, version, release), ...}
        self.conflicts = {}  # -||-
        self.obsoletes = {}  # -||-
        self.requires  = {}  # {'filename': (flags, epoch, version, release, pre), ...}
        self.files  = set()  # primary_files
        self.dirs   = set()  # primary_dirs
        self.ghosts = set()  # primary_ghosts
        if not self.DIFF_ATTR:
            self.DIFF_ATTR = self.__dict__.keys()

    def pprint(self):
        Package.pprint(self)
        msg  = "Time - File: %s | Build: %s\n" % \
                    (self.time_file, self.time_build)
        msg += "Size - Package: %s | Installed: %s | Archive: %s\n" % \
                    (self.size_package, self.size_installed, self.size_archive)
        print msg


class PrimaryMetadata(Metadata):

    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)

    def checksum_to_name(self, checksum):
        if checksum in self.chksum_to_name:
            return self.chksum_to_name[checksum]
        return None

    def name_to_checksum(self, name):
        if name in self.name_to_chksum:
            return self.name_to_chksum[name]
        return None

    def get_package_names(self):
        return set(self.name_to_chksum.keys())
