from yum_metadata_diff.diff_objects import MetadataDiff


class MetadataItem(object):

    DIFF_CLASS = None
    DIFF_ATTR = tuple()
    NONE_AND_EMPTY_ARE_SAME = tuple()

    def __init__(self):
        pass

    def diff(self, other):
        if not self.DIFF_CLASS:
            raise NotImplementedError("DIFF_CLASS is not set for self %s" % \
                                      self)

        ppd = self.DIFF_CLASS()

        # Compare only what can be compared
        diff_attrs = set(self.DIFF_ATTR).intersection(set(other.DIFF_ATTR))

        for key in diff_attrs:
            a = getattr(self, key)
            b = getattr(other, key)

            ### Exceptions in comparsion

            # None and "" have same meaning
            if key in self.NONE_AND_EMPTY_ARE_SAME:
                if not a and not b:
                    continue  # This is OK

            ### End of exceptions

            if a != b:
                ppd.add_difference(key, a, b, "Attribute")
        if ppd:
            return ppd
        return None


class Metadata(object):

    def __init__(self, path=None, archpath=None):
        self.path = path         # Path to metadata file
        self.archpath = archpath # Path to original compressed metadata file
        self.items = {}          # for a package the key is checksum

    def __iter__(self):
        return self.items.itervalues()

    def __contains__(self, key):
        return key in self.items

    def __getitem__(self, key):
        return self.items[key]

    def append(self, key, item):
        if key in self.items:
            print "WARNING: Multiple items with the same key \"%s\":\n" \
                  "  1: %s\n  2: %s\n" % (key, self.items[key], item)
            return
        self.items[key] = item

    def get(self, key):
        return self.items.get(key)

    def diff(self, other):
        pmd = MetadataDiff()
        a = set(self.items.keys())
        b = set(other.items.keys())
        # Check package lists
        if a != b:
            pmd.missing_items = a - b
            pmd.added_items = b - a
        # Check attributes of items
        for pkg in a.intersection(b):
            pkg_a = self.items[pkg]
            pkg_b = other.items[pkg]
            pkg_diff = pkg_a.diff(pkg_b)
            if pkg_diff:
                pmd.changed_items.add(pkg)
                pmd.items_diffs[pkg] = pkg_diff
        if pmd:
            return pmd
        return None

    def keys(self):
        return self.items.keys()
