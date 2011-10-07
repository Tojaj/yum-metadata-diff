#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import run_tests # set sys.path

from repodiff.package import Package
from repodiff.metadata import Metadata
from repodiff.diff_objects import PackageDiff


class TestMetadata(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_metadata(self):
        chksum_a = "abc"
        name_a   = "foo"
        chksum_b = "dfg"
        name_b   = "bar"

        class TestPackage(Package):
            DIFF_ATTR = ('checksum', 'name')

        # Both metadata are same (contains same packages)
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_a
        pkg2.name = name_a
        md1 = Metadata()
        md1.append(pkg1)
        md2 = Metadata()
        md2.append(pkg2)
        diff = md1.diff(md2)
        self.assertFalse(diff)

        md1 = Metadata()
        md2 = Metadata()
        diff = md1.diff(md2)
        self.assertFalse(diff)

        # Metadata are different (pkg2 has one more package)
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_b
        pkg2.name = name_b
        md1 = Metadata()
        md1.append(pkg1)
        md2 = Metadata()
        md2.append(pkg1)
        md2.append(pkg2)
        diff = md1.diff(md2)
        self.assertTrue(diff)
        self.assertEqual(diff.changed_packages, set([]))
        self.assertEqual(diff.missing_packages, set([]))
        self.assertEqual(diff.added_packages, set([chksum_b]))

        md1 = Metadata()
        md2 = Metadata()
        md2.append(pkg2)
        diff = md1.diff(md2)
        self.assertTrue(diff)
        self.assertEqual(diff.changed_packages, set([]))
        self.assertEqual(diff.missing_packages, set([]))
        self.assertEqual(diff.added_packages, set([chksum_b]))

        # Metadata are different (pkg1 has one more package)
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_b
        pkg2.name = name_b
        md1 = Metadata()
        md1.append(pkg1)
        md1.append(pkg2)
        md2 = Metadata()
        md2.append(pkg1)
        diff = md1.diff(md2)
        self.assertTrue(diff)
        self.assertEqual(diff.added_packages, set([]))
        self.assertEqual(diff.changed_packages, set([]))
        self.assertEqual(diff.missing_packages, set([chksum_b]))

        md1 = Metadata()
        md1.append(pkg2)
        md2 = Metadata()
        diff = md1.diff(md2)
        self.assertTrue(diff)
        self.assertEqual(diff.added_packages, set([]))
        self.assertEqual(diff.changed_packages, set([]))
        self.assertEqual(diff.missing_packages, set([chksum_b]))

        # Metadata are different (package has changed attribute)
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_a
        pkg2.name = name_b
        md1 = Metadata()
        md1.append(pkg1)
        md2 = Metadata()
        md2.append(pkg2)
        diff = md1.diff(md2)
        self.assertTrue(diff)
        self.assertEqual(diff.added_packages, set([]))
        self.assertEqual(diff.missing_packages, set([]))
        self.assertEqual(diff.changed_packages, set([chksum_a]))
        self.assertTrue(chksum_a in diff.packages_diffs)
        self.assertTrue(isinstance(diff.packages_diffs[chksum_a], PackageDiff))


if __name__ == "__main__":
    unittest.main()
