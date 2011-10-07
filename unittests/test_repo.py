#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import run_tests # set sys.path
from repodiff.repo import OneRepo, CompleteRepo


class MetadataMock(object):
    def __init__(self, checksums=None, packages=None):
        self.checksums = checksums
        self.packages = packages

    def get_package_checksums(self):
        return set(self.checksums)

    def get_package_names(self):
        return set(self.packages)

    def diff(self, _):
        return None


class TestOneRepo(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_sanity(self):
        pri = fil = oth = MetadataMock(checksums=('aaa', 'bbb'))
        repo = OneRepo(pri, fil, oth)
        self.assertTrue(repo.check_sanity())

        pri = fil = MetadataMock(checksums=('aaa', 'bbb'))
        oth = MetadataMock(checksums=('aaa'))
        repo = OneRepo(pri, fil, oth)
        self.assertFalse(repo.check_sanity())

        pri = oth = MetadataMock(checksums=('aaa', 'bbb'))
        fil = MetadataMock(checksums=('aaa'))
        repo = OneRepo(pri, fil, oth)
        self.assertFalse(repo.check_sanity())

    def test_packages(self):
        packages = set(('a', 'b'))
        pri = MetadataMock(packages=packages)
        repo = OneRepo(pri, None, None)
        self.assertEqual(repo.packages(), packages)

    def test_checksums(self):
        checksums = set(('abc', 'efg'))
        pri = MetadataMock(checksums=checksums)
        repo = OneRepo(pri, None, None)
        self.assertEqual(repo.checksums(), checksums)


class TestCompleteRepo(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_sanity(self):
        # Repos are same
        checksums = set(['123', '456'])
        packages = set(['abc', 'def'])
        xmlpri = xmlfil = xmloth = MetadataMock(checksums=checksums,
                                                packages=packages)
        xmlrepo = OneRepo(xmlpri, xmlfil, xmloth)
        sqlpri = sqlfil = sqloth = MetadataMock(checksums=checksums,
                                                packages=packages)
        sqlrepo = OneRepo(sqlpri, sqlfil, sqloth)
        repo = CompleteRepo(xmlrepo, sqlrepo)
        self.assertTrue(repo.check_sanity())

        # XML repo is not sane
        checksums = set(['123', '456'])
        packages = set(['abc', 'def'])
        xmlpri = MetadataMock(checksums=set(['123', '789']),
                                packages=packages)
        xmlfil = xmloth = MetadataMock(checksums=checksums,
                                        packages=packages)
        xmlrepo = OneRepo(xmlpri, xmlfil, xmloth)
        sqlpri = sqlfil = sqloth = MetadataMock(checksums=checksums,
                                                packages=packages)
        sqlrepo = OneRepo(sqlpri, sqlfil, sqloth)
        repo = CompleteRepo(xmlrepo, sqlrepo)
        self.assertFalse(repo.check_sanity())

        # Sqlite repo is not sane
        checksums = set(['123', '456'])
        packages = set(['abc', 'def'])
        xmlpri = xmlfil = xmloth = MetadataMock(checksums=checksums,
                                        packages=packages)
        xmlrepo = OneRepo(xmlpri, xmlfil, xmloth)
        sqlpri = MetadataMock(checksums=set(['123', '789']),
                                packages=packages)
        sqlfil = sqloth = MetadataMock(checksums=checksums,
                                                packages=packages)
        sqlrepo = OneRepo(sqlpri, sqlfil, sqloth)
        repo = CompleteRepo(xmlrepo, sqlrepo)
        self.assertFalse(repo.check_sanity())

        # Sqlite and xml is different
        packages = set(['abc', 'def'])
        xmlpri = xmlfil = xmloth = MetadataMock(checksums=set(['123', '456']),
                                        packages=packages)
        xmlrepo = OneRepo(xmlpri, xmlfil, xmloth)
        sqlpri = sqlfil = sqloth = MetadataMock(checksums= set(['123', '789']),
                                                packages=packages)
        sqlrepo = OneRepo(sqlpri, sqlfil, sqloth)
        repo = CompleteRepo(xmlrepo, sqlrepo)
        self.assertFalse(repo.check_sanity())


if __name__ == "__main__":
    unittest.main()
