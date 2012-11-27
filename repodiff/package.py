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

        # Compare only what can be compared
        diff_attrs = set(self.DIFF_ATTR).intersection(set(other.DIFF_ATTR))

        for key in diff_attrs:
            a = getattr(self, key)
            b = getattr(other, key)

            # Exceptions in comparsion

            # None (NULL) and "" have same meaning
            if key in ("location_base", "vendor", "description",
                       "sourcerpm"):
                if a is None and b == '':
                    continue  # This is OK

            # End of exceptions

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
