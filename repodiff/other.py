from repodiff.package import Package
from repodiff.metadata import Metadata


class OtherPackage(Package):

    DIFF_ATTR = ('checksum', 'changelogs')

    def __init__(self):
        Package.__init__(self)
        self.arch = ""      #-\
        #self.name = ""     #--\
        self.version = ""   #---- This info is available only in XML
        self.epoch = ""     #--/
        self.release = ""   #-/
        self.changelogs = set()  # set([(author, date, text), ...])


class OtherMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)

