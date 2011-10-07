from repodiff.package import Package
from repodiff.metadata import Metadata


class FilelistsPackage(Package):

    DIFF_ATTR = ('checksum', 'files', 'dirs', 'ghosts')

    def __init__(self):
        Package.__init__(self)
        self.arch = ""       #-\
        #self.name = ""      #--\
        self.version = ""    #---- This information is available only in XML
        self.epoch = ""      #--/
        self.release = ""    #-/
        self.files = set()
        self.dirs = set()
        self.ghosts = set()


class FilelistsMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)

