from repodiff.diff_objects import MetadataDiff


class Metadata(object):
    def __init__(self, path=None, archpath=None):
        self.path     = path      # Path to metadata file
        self.archpath = archpath  # Path to original compressed metadata file
        self.packages = {}        # key is checksum
        self.name_to_chksum = {}
        self.chksum_to_name = {}

    def __iter__(self):
        return self.packages.itervalues()

    def append(self, ppackage):
        if ppackage.checksum in self.packages:
            print "WARNING: Multiple items with the same checksum %s " \
                  "(Names are %s and %s)" % (ppackage.checksum, ppackage.name,
                  self.packages[ppackage.checksum].name)
            return
        self.packages[ppackage.checksum] = ppackage
        if ppackage.name:
            self.name_to_chksum[ppackage.name] = ppackage.checksum
            self.chksum_to_name[ppackage.checksum] = ppackage.name

    def get(self, name):
        key = self.name_to_chksum.get(name)
        if not key:
            return None
        return self.packages.get(key)

    def diff(self, other):
        pmd = MetadataDiff()
        a = set(self.packages.keys())
        b = set(other.packages.keys())
        # Check package lists
        if a != b:
            pmd.missing_packages = a - b
            pmd.added_packages   = b - a
        # Check attributes of packages
        for pkg in a.intersection(b):
            pkg_a = self.packages[pkg]
            pkg_b = other.packages[pkg]
            pkg_diff = pkg_a.diff(pkg_b)
            if pkg_diff:
                pmd.changed_packages.add(pkg)
                pmd.packages_diffs[pkg] = pkg_diff
        if pmd:
            return pmd
        return None

    def get_package_checksums(self):
        return set(self.packages.keys())
