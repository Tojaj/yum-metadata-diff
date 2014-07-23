Repodiff
========
Repodiff is a python library and an utility to check sanity of metadata of
a yum repository and comparation of two repositories.

Example usage:
==============

Sanity check
------------

    python repo_diff.py --verbose test_repos/different_xml_and_sql/


Comparation
-----------

    python repo_diff.py --compare test_repos/sane_repo test_repos/sane_repo_2/


