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
        parser.error("You must specify a directory with repodata.")
    if options.compare and len(args) != 2:
        parser.error("With \"--compare\" you must specify exactly two directories.")
    if not options.compare and len(args) != 1:
        parser.error("Only one single directory can be specified for --check "
                      "option. (Didn't you forget to use --compare?)")

    repodir = args[0]
    verbose = options.verbose

    if options.compare:
        # Compare metadata of two repositories
        repodir2 = args[1]
        cr1 = completerepo_factory(repodir)
        cr2 = completerepo_factory(repodir2)
        diff = cr1.diff(cr2)
        if diff:
            print diff.pprint()
            print "Repos are not same"
            sys.exit(2)
    else:
        # Sanity check of metadata
        cr1 = completerepo_factory(repodir)
        ret = cr1.check_sanity(verbose=verbose)
        if not ret:
            print "Repodata is not sane"
            sys.exit(2)

    sys.exit(0)
