#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import run_tests # set sys.path
from repodiff.diff_objects import PackageDiff, MetadataDiff


class TestPackageDiff(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_packagediff(self):
        pkgdiff = PackageDiff()
        self.assertFalse(pkgdiff)
        self.assertEqual(pkgdiff.changed_attributes, set([]))
        self.assertEqual(pkgdiff.attr_values, {})

        key = "attr1"
        val1 = "foo"
        val2 = "bar"
        pkgdiff.changed_attributes.add(key)
        pkgdiff.attr_values[key] = (val1, val2)
        self.assertTrue(pkgdiff)
        self.assertEqual(pkgdiff.changed_attributes, set([key]))
        self.assertEqual(pkgdiff.attr_values, {key: (val1, val2)})


class TestMetadataDiff(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_metadatadiff(self):
        mdiff = MetadataDiff()
        self.assertFalse(mdiff)
        self.assertEqual(mdiff.missing_packages, set([]))
        self.assertEqual(mdiff.added_packages, set([]))
        self.assertEqual(mdiff.changed_packages, set([]))
        self.assertEqual(mdiff.packages_diffs, {})

        mdiff = MetadataDiff()
        mdiff.missing_packages.add("pkg")
        self.assertTrue(mdiff)

        mdiff = MetadataDiff()
        mdiff.added_packages.add("pkg")
        self.assertTrue(mdiff)

        mdiff = MetadataDiff()
        mdiff.changed_packages.add("pkg")
        self.assertTrue(mdiff)

        mdiff = MetadataDiff()
        a_pkg = "pkg1"
        b_pkg = "pkg2"
        c_pkg = "pkg3"
        mdiff.missing_packages.add(a_pkg)
        mdiff.added_packages.add(b_pkg)
        mdiff.changed_packages.add(c_pkg)
        pd = PackageDiff()
        mdiff.packages_diffs[c_pkg] = pd
        self.assertTrue(mdiff)
        self.assertEqual(mdiff.missing_packages, set([a_pkg]))
        self.assertEqual(mdiff.added_packages, set([b_pkg]))
        self.assertEqual(mdiff.changed_packages, set([c_pkg]))
        self.assertEqual(mdiff.packages_diffs, {c_pkg: pd})


if __name__ == "__main__":
    unittest.main()
