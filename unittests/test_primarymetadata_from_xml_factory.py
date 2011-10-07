#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import os.path
import unittest
import tempfile
import run_tests # set sys.path
from repodiff import primarymetadata_from_xml_factory


CHECKSUM = '123456'

PRIMARY_DICT = {'checksum': CHECKSUM,
                'name': 'foobar',
                'arch': 'i386',
                'epoch': '0',
                'version': '2.0.0',
                'release': '1',
                'checksum_type': 'sha256',
                'summary': 'foobar adfsafd',
                'description': 'asdfdsfadsfsafa',
                'packager': 'anybody',
                'url': 'localhost',
                'time_build': 11,
                'time_file': 22,
                'size_package': 111,
                'size_installed': 222,
                'size_archive': 333,
                'location': 'loc',
                'license': 'gpl',
                'vendor': 'vendor',
                'group': 'group',
                'buildhost': 'buildhost',
                'sourcerpm': 'source',
                'header_start': 1,
                'header_end': 22,
                }
PRIMARY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns="http://linux.duke.edu/metadata/common" xmlns:rpm="http://linux.duke.edu/metadata/rpm" packages="1">
<package type="rpm">
  <name>%(name)s</name>
  <arch>%(arch)s</arch>
  <version epoch="%(epoch)s" ver="%(version)s" rel="%(release)s"/>
  <checksum type="%(checksum_type)s" pkgid="YES">%(checksum)s</checksum>
  <summary>%(summary)s</summary>
  <description>%(description)s</description>
  <packager>%(packager)s</packager>
  <url>%(url)s</url>
  <time file="%(time_file)s" build="%(time_build)s"/>
  <size package="%(size_package)s" installed="%(size_installed)s" archive="%(size_archive)s"/>
  <location href="%(location)s"/>
  <format>
    <rpm:license>%(license)s</rpm:license>
    <rpm:vendor>%(vendor)s</rpm:vendor>
    <rpm:group>%(group)s</rpm:group>
    <rpm:buildhost>%(buildhost)s</rpm:buildhost>
    <rpm:sourcerpm>%(sourcerpm)s</rpm:sourcerpm>
    <rpm:header-range start="%(header_start)s" end="%(header_end)s"/>
    <rpm:provides>
      <rpm:entry name="aaa" flags="EQ" epoch="0" ver="2.0.0" rel="1"/>
    </rpm:provides>
    <rpm:conflicts>
      <rpm:entry name="con" flags="EQ" epoch="2" ver="2.2.0" rel="4"/>
    </rpm:conflicts>
    <rpm:obsoletes>
      <rpm:entry name="obs" flags="EQ" epoch="1" ver="2.1.0" rel="2"/>
    </rpm:obsoletes>
    <rpm:requires>
      <rpm:entry name="bbb" flags="EQ" epoch="0" ver="1.0.0" rel="1" pre="1"/>
    </rpm:requires>
    <file>file1</file>
    <file type="dir">dir1</file>
    <file type="ghost">ghost1</file>
  </format>
</package>
</metadata>
""" % PRIMARY_DICT


class TestXMLFactory(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.mktemp()
        open(self.tmpfile, 'w').write(PRIMARY_XML)

    def tearDown(self):
        os.remove(self.tmpfile)

    def test_primary_factory(self):
        a = primarymetadata_from_xml_factory(self.tmpfile)

        package = a.packages[CHECKSUM]
        for key in PRIMARY_DICT:
            self.assertEqual(getattr(package, key), PRIMARY_DICT[key])
        self.assertEqual(package.provides, {'aaa': ('EQ', "0", "2.0.0", "1")})
        self.assertEqual(package.obsoletes, {'obs': ('EQ', "1", "2.1.0", "2")})
        self.assertEqual(package.conflicts, {'con': ('EQ', "2", "2.2.0", "4")})
        self.assertEqual(package.requires, {'bbb': ('EQ', "0", "1.0.0", "1", True)})
        self.assertEqual(package.files, set(['file1']))
        self.assertEqual(package.dirs, set(['dir1']))
        self.assertEqual(package.ghosts, set(['ghost1']))

if __name__ == "__main__":
    unittest.main()
