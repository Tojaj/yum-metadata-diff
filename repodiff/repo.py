from diff_objects import OneRepoDiff, CompleteRepoDiff
from pprint import pformat

class OneRepo(object):
    """Class represent metadata set (primary + filelistst + other)
    for one metadata type (xml or sqlite)"""

    def __init__(self, primary, filelists, other):
        self.pri = primary
        self.fil = filelists
        self.oth = other

    def checksum_to_name(self, chksum):
        """Translate checksum to name."""
        return self.pri.checksum_to_name(chksum)

    def name_to_checksum(self, name):
        """Translate name to checksum."""
        return self.pri.name_to_checksum(name)

    def check_sanity(self, verbose=False):
        """Check if packages in primary, filelists 
        and other metadata files correspond."""
        is_ok = True
        pri_keys = self.pri.get_package_checksums()
        fil_keys = self.fil.get_package_checksums()
        oth_keys = self.oth.get_package_checksums()
        if pri_keys != fil_keys:
            if verbose:
                print "Packages in PRIMARY and FILELISTS are different:"
                pri = pri_keys - fil_keys
                if pri:
                    print "  Filelists missing packages:"
                    print "    %s" % pformat(pri)
                fil = fil_keys - pri_keys
                if fil:
                    print "  Filelists redundant packages:"
                    print "    %s" % pformat(fil)
            is_ok = False
        if pri_keys != oth_keys:
            if verbose:
                print "Packages in PRIMARY and OTHER are different:"
                pri = pri_keys - oth_keys
                if pri:
                    print "  Other missing packages:"
                    print "    %s" % pformat(pri)
                oth = oth_keys - pri_keys
                if oth:
                    print "  Other redundant packages:"
                    print "    %s" % pformat(oth)
            is_ok = False
        return is_ok

    def packages(self):
        return self.pri.get_package_names()

    def checksums(self):
        return self.pri.get_package_checksums()

    def diff(self, other):
        chksum_to_name_dicts = (self.pri.chksum_to_name,
                                other.pri.chksum_to_name)

        onerepo_diff = OneRepoDiff(chksum_to_name_dicts=chksum_to_name_dicts)
        diff = self.pri.diff(other.pri)
        if diff:
            onerepo_diff.pri_diff = diff
        diff = self.fil.diff(other.fil)
        if diff:
            onerepo_diff.fil_diff = diff
        diff = self.oth.diff(other.oth)
        if diff:
            onerepo_diff.oth_diff = diff
        return onerepo_diff


class CompleteRepo(object):

    def __init__(self, xml_repo, sqlite_repo=None):
        self.xml_rep = xml_repo
        self.sql_rep = sqlite_repo

    def vprint(self, text, verbose=True):
        if verbose:
            print text

    def check_sanity(self, verbose=False):
        # Check XML metadata sanity
        is_ok = True
        self.vprint("> Checking XML metadata sanity...", verbose)
        if not self.xml_rep.check_sanity(verbose):
            self.vprint("XML metadata sanity check FAILED", verbose)
            is_ok = False

        if not self.sql_rep:
            # Nothing to do, we have only one sane metadata type
            return True

        # Check Sqlite metadata sanity
        self.vprint("> Checking Sqlite metadata sanity...", verbose)
        if not self.sql_rep.check_sanity(verbose):
            self.vprint("Sqlite repo sanity check FAILED", verbose)
            is_ok = False

        # Check that both metadata (xml and sqlite) have same packages (by names)
        self.vprint("> Checking that packages in both metadatas are same (by name)...", verbose)
        xml_pkg_set = self.xml_rep.packages()
        sql_pkg_set = self.sql_rep.packages()
        if xml_pkg_set != sql_pkg_set:
            if verbose:
                self.vprint("Sets of packages in xml and sqlite are DIFFERENT", verbose)
                self.vprint("  Packages in xml but not in sqlite:", verbose)
                for chksum in (sql_pkg_set - xml_pkg_set):
                    self.vprint("    %s" % self.xml_rep.checksum_to_name(chksum), verbose)
                self.vprint("  Packages in sqlite but not in xml:", verbose)
                for chksum in (sql_pkg_set - xml_pkg_set):
                    self.vprint("    %s" % self.xml_rep.checksum_to_name(chksum), verbose)
            return False

        # Check that both metadata (xml and sqlite) have same packages (by checksums)
        self.vprint("> Checking that packages in both metadatas are same (by checksum)...", verbose)
        xml_chksum_set = self.xml_rep.checksums()
        sql_chksum_set = self.sql_rep.checksums()
        if xml_chksum_set != sql_chksum_set:
            if verbose:
                self.vprint("Sets of packages in xml and sqlite are same, " \
                      "but at least one checksum is DIFFERENT.", verbose)
                self.vprint("Package(s) with different checksum(s):", verbose)
                for chksum in xml_chksum_set - sql_chksum_set:
                    self.vprint("  %s" % self.xml_rep.checksum_to_name(chksum), verbose)
            return False

        # Compare individual repodata
        self.vprint("> Checking individual metadata...", verbose)
        diff = self.xml_rep.pri.diff(self.sql_rep.pri)
        if diff:
            if verbose:
                self.vprint("XML and Sqlite primary repodata are different:", verbose)
                self.vprint(diff.pprint(), verbose)
            is_ok = False
        diff = self.xml_rep.fil.diff(self.sql_rep.fil)
        if diff:
            if verbose:
                self.vprint("XML and Sqlite filelists repodata are different:", verbose)
                self.vprint(diff.pprint(), verbose)
            is_ok = False
        diff = self.xml_rep.oth.diff(self.sql_rep.oth)
        if diff:
            if verbose:
                self.vprint("XML and Sqlite other repodata are different:", verbose)
                self.vprint(diff.pprint(), verbose)
            is_ok = False

        return is_ok

    def diff(self, other):
        completerepo_diff = CompleteRepoDiff()
        diff = self.xml_rep.diff(other.xml_rep)
        if diff:
            completerepo_diff.xml_repo_diff = diff
        if self.sql_rep and other.sql_rep:
            diff  = self.sql_rep.diff(other.sql_rep)
            if diff:
                completerepo_diff.sql_repo_diff = diff
        else:
            if not self.sql_rep:
                print "Warning: First repo has not Sqlite database!"
            else:
                print "Warning: Second repo has not Sqlite database!"
        return completerepo_diff
