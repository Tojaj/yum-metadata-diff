from repodiff.package import Package
from repodiff.metadata import Metadata


class FilelistsPackage(Package):

    DIFF_ATTR = ('checksum', 'files', 'dirs', 'ghosts')

    def __init__(self):
        Package.__init__(self)
        #self.arch = ""       #-\
        #self.name = ""       #--\
        #self.version = ""    #---- This information is available only in XML
        #self.epoch = ""      #--/
        #self.release = ""    #-/
        self.files = set()
        self.dirs = set()
        self.ghosts = set()


class FilelistsDbPackage(FilelistsPackage):

    DIFF_ATTR = ('checksum', 'files', 'dirs', 'ghosts',
                 'dbdirectories', 'files_db', 'dirs_db', 'ghosts_db')

    def __init__(self):
        FilelistsPackage.__init__(self)
        self.dbdirectories = list() # Directories from filelist db table
        self.files_db = set() # Raw splited files from db
        self.dirs_db = set() # Raw splited dirs from db
        self.ghosts_db = set() # Ras splited ghosts from db


class FilelistsMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        Metadata.__init__(self, *args, **kwargs)

