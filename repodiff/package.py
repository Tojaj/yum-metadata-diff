import pprint
from repodiff.diff_objects import PackageDiff

class Package(object):

    DIFF_CLASS = PackageDiff
    DIFF_ATTR = ('checksum')

    def __init__(self):
        self.checksum = ''  # pkgid
        self.name = ''

    def diff(self, other):
        ppd = self.DIFF_CLASS()
        for key in self.DIFF_ATTR:
            a = getattr(self, key)
            b = getattr(other, key)
            if a != b:
                ppd.changed_attributes.add(key)
                ppd.attr_values[key] = (a, b)
        if ppd:
            return ppd
        return None

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def pprint(self):
        msg  = "%s (%s)\n" % (self.name, self.checksum)
        print msg
