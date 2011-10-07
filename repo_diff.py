#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser
from repodiff import completerepo_factory


if __name__ == "__main__":
    parser = OptionParser('usage: %prog [options].. <repodata_directory>..')
    parser.add_option('-c', '--check', help="Check repodata sanity. (Default)",
                        action='store_true', default=True)
    parser.add_option('-d', '--compare', help="Compare two repodata.",
                        action='store_true')
    parser.add_option('-v', '--verbose', help="Show verbose output.",
                        action='store_true')
    options, args = parser.parse_args()

    repodir = None
    repodir2 = None

    if len(args) < 1:
        print "Error: You must specify a directory with repodata."
        sys.exit(1)
    if options.compare and len(args) != 2:
        print "Error: With \"--compare\" you must specify exactly two directories."
        sys.exit(1)

    repodir = args[0]
    verbose = options.verbose

    # Compare metadata of two repositories
    if options.compare:
        repodir2 = args[1]
        cr1 = completerepo_factory(repodir)
        cr2 = completerepo_factory(repodir2)
        ret = cr1.diff(cr2)
        if not ret:
            print "Repos are not same"
            sys.exit(2)
        sys.exit(0)

    # Sanity check of metadata
    cr1 = completerepo_factory(repodir)
    ret = cr1.check_sanity(verbose=verbose)
    if not ret:
        print "Repodata are not sane"
        sys.exit(2)
    sys.exit(0)
