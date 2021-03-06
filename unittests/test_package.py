#!/usr/bin/python
# -*- coding: utf-8 -*-


import unittest
import run_tests # set sys.path
from repodiff.package import Package


class TestPackage(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_packag(self):
        chksum_a = "foo"
        name_a = "bar"
        chksum_b = "foobbb"
        name_b = "barbbb"

        class TestPackage(Package):
            DIFF_ATTR = ('checksum', 'name')

        # Both packages are same
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_a
        pkg2.name = name_a
        self.assertFalse(pkg1.diff(pkg2))

        # Packages are completly different
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_b
        pkg2.name = name_b
        diff = pkg1.diff(pkg2)
        self.assertTrue(diff)
        self.assertEqual(diff.differences,
                        [('checksum', 'foo', 'foobbb', 'Attribute', None),
                         ('name', 'bar', 'barbbb', 'Attribute', None)])

        # Packages have one same and one different attribute
        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_a
        pkg2.name = name_b
        diff = pkg1.diff(pkg2)
        self.assertTrue(diff)

        pkg1 = TestPackage()
        pkg1.checksum = chksum_a
        pkg1.name = name_a
        pkg2 = TestPackage()
        pkg2.checksum = chksum_b
        pkg2.name = name_a
        diff = pkg1.diff(pkg2)
        self.assertTrue(diff)

if __name__ == "__main__":
    unittest.main()
