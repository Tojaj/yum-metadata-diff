import os
import sys
import bz2
import gzip
import shutil
import os.path
import liblzma
import tempfile
try:
    import sqlite3 as sqlite
except ImportError:
    import sqlite

from lxml import etree

from yum_metadata_diff.repo import OneRepo, CompleteRepo
from yum_metadata_diff.other import OtherMetadata, OtherPackage
from yum_metadata_diff.primary import PrimaryMetadata, PrimaryPackage
from yum_metadata_diff.repomd import RepomdMetadata, RepomdItem
from yum_metadata_diff.filelists import FilelistsMetadata, FilelistsPackage
from yum_metadata_diff.filelists import FilelistsDbPackage


# namespace
PRI_NS = "{http://linux.duke.edu/metadata/common}"
FIL_NS = "{http://linux.duke.edu/metadata/filelists}"
OTH_NS = "{http://linux.duke.edu/metadata/other}"
MD_NS = "{http://linux.duke.edu/metadata/repo}"


class XmlRepo(object):
    pass


class Repo(object):
    pass


class MyElement(object):
    def __init__(self, element):
        self.element = element

    def get(self, name, default=None):
        res = self.element.get(name, default)
        if isinstance(res, basestring):
            return unicode(res)
        return res

    @property
    def text(self):
        res = self.element.text
        if isinstance(res, basestring):
            return unicode(res)
        return res

    def __getattr__(self, name):
        return getattr(self.element, name)

    def __iter__(self):
        return self.element.__iter__()


#
# XML
#


def _parse_pco(elem, requires=False):
    req_set = set([])
    for felem in elem:
        felem = MyElement(felem)
        if felem.tag.endswith("entry"):
            res = (felem.get("name"),
                   felem.get("flags"),
                   felem.get("epoch"),
                   felem.get("ver"),
                   felem.get("rel"))
            if requires:
                res += (bool(int(felem.get("pre", 0))),)
        req_set.add(res)
    return req_set


def primarymetadata_from_xml_factory(xmlpath, archpath):
    pri_obj = PrimaryMetadata(xmlpath, archpath)
    for _, elements in etree.iterparse(xmlpath, tag="%spackage" % PRI_NS):
        elements = MyElement(elements)
        pp = PrimaryPackage()
        for elem in elements:
            elem = MyElement(elem)
            if elem.tag.endswith("name"):
                pp.name = elem.text
            elif elem.tag.endswith("arch"):
                pp.arch = elem.text
            elif elem.tag.endswith("version"):
                pp.epoch = elem.get("epoch")
                pp.version = elem.get("ver")
                pp.release = elem.get("rel")
            elif elem.tag.endswith("checksum"):
                pp.checksum_type = elem.get("type")
                pp.checksum = elem.text
            elif elem.tag.endswith("summary"):
                pp.summary = elem.text
            elif elem.tag.endswith("description"):
                pp.description = elem.text
            elif elem.tag.endswith("packager"):
                pp.packager = elem.text
            elif elem.tag.endswith("url"):
                pp.url = elem.text
            elif elem.tag.endswith("time"):
                pp.time_file = int(elem.get("file"))
                pp.time_build = int(elem.get("build"))
            elif elem.tag.endswith("size"):
                pp.size_package = int(elem.get("package"))
                pp.size_installed = int(elem.get("installed"))
                pp.size_archive = int(elem.get("archive"))
            elif elem.tag.endswith("location"):
                pp.location = elem.get("href")
                pp.location_base = elem.get("{http://www.w3.org/XML/1998/namespace}base")
            elif elem.tag.endswith("format"):
                for felem in elem:
                    if felem.tag.endswith("license"):
                        pp.license = felem.text
                    elif felem.tag.endswith("vendor"):
                        pp.vendor = felem.text
                    elif felem.tag.endswith("group"):
                        pp.group = felem.text
                    elif felem.tag.endswith("buildhost"):
                        pp.buildhost = felem.text
                    elif felem.tag.endswith("sourcerpm"):
                        pp.sourcerpm = felem.text
                    elif felem.tag.endswith("header-range"):
                        pp.header_start = int(felem.get("start"))
                        pp.header_end = int(felem.get("end"))
                    elif felem.tag.endswith("provides"):
                        pp.provides = _parse_pco(felem)
                    elif felem.tag.endswith("conflicts"):
                        pp.conflicts = _parse_pco(felem)
                    elif felem.tag.endswith("obsoletes"):
                        pp.obsoletes = _parse_pco(felem)
                    elif felem.tag.endswith("requires"):
                        pp.requires = _parse_pco(felem, requires=True)
                    elif felem.tag.endswith("file"):
                        if felem.get("type") == "dir":
                            pp.dirs.add(felem.text)
                        elif felem.get("type") == "ghost":
                            pp.ghosts.add(felem.text)
                        else:
                            pp.files.add(felem.text)
        elements.clear()
        pri_obj.append(pp.checksum, pp)
    return pri_obj


def filelistsmetadata_from_xml_factory(xmlpath, archpath):
    fil_obj = FilelistsMetadata(xmlpath, archpath)
    for _, elements in etree.iterparse(xmlpath, tag="%spackage" % FIL_NS):
        elements = MyElement(elements)
        fp = FilelistsPackage()
        fp.checksum = elements.get("pkgid")
        fp.arch = elements.get("arch")
        fp.name = elements.get("name")
        for elem in elements:
            elem = MyElement(elem)
            if elem.tag.endswith("version"):
                fp.epoch = elem.get("epoch")
                fp.version = elem.get("ver")
                fp.release = elem.get("rel")
            elif elem.tag.endswith("file"):
                if elem.get("type") == "dir":
                    fp.dirs.add(elem.text)
                elif elem.get("type") == "ghost":
                    fp.ghosts.add(elem.text)
                else:
                    fp.files.add(elem.text)
        elements.clear()
        fil_obj.append(fp.checksum, fp)
    return fil_obj


def othermetadata_from_xml_factory(xmlpath, archpath):
    oth_obj = OtherMetadata(xmlpath, archpath)
    for _, elements in etree.iterparse(xmlpath, tag="%spackage" % OTH_NS):
        elements = MyElement(elements)
        op = OtherPackage()
        op.checksum = elements.get("pkgid")
        op.arch = elements.get("arch")
        op.name = elements.get("name")
        for elem in elements:
            elem = MyElement(elem)
            if elem.tag.endswith("version"):
                op.epoch = elem.get("epoch")
                op.version = elem.get("ver")
                op.release = elem.get("rel")
            elif elem.tag.endswith("changelog"):
                op.changelogs.append((elem.get("author"), int(elem.get("date")), elem.text))
        elements.clear()
        oth_obj.append(op.checksum, op)
    return oth_obj


#
# Sqlite
#


def primarymetadata_from_sqlite_factory(sqlitepath, archpath):
    pri_obj = PrimaryMetadata(sqlitepath, archpath)

    con = sqlite.Connection(sqlitepath)
    pri_cur = con.cursor()

    col_packages = ['checksum', 'name', 'arch', 'version', 'epoch', 'release',
                    'summary', 'description', 'url', 'time_file', 'time_build',
                    'license', 'vendor', 'group', 'buildhost', 'sourcerpm',
                    'header_start', 'header_end', 'packager', 'size_package',
                    'size_installed', 'size_archive', 'location', 'location_base',
                    'checksum_type']

    pri_cur.execute('SELECT * FROM packages')
    for row in pri_cur:
        pp = PrimaryPackage()

        uid = row[0]
        for key, val in zip(col_packages, row[1:]):
            setattr(pp, key, val)

        if pp.location_base == None:
            pp.location_base = ''

        cur = con.cursor()
        # provides, obsoletes, conflicts
        for pco in ('obsoletes', 'provides', 'conflicts'):
            pco_set = set([])
            cur.execute('SELECT * FROM %s WHERE pkgKey=?' % pco, (uid,))
            for name, flag, epoch, ver, rel, _ in cur:
                pco_set.add((name, flag, epoch, ver, rel))
            setattr(pp, pco, pco_set)

        # requires
        req_set = set([])
        cur.execute('SELECT * FROM requires WHERE pkgKey=?', (uid,))
        for name, flag, epoch, ver, rel, _, pre in cur:
            if pre == 'TRUE':
                pre = True
            else:
                pre = False
            req_set.add((name, flag, epoch, ver, rel, pre))
        setattr(pp, 'requires', req_set)

        #files
        files = set([])
        dirs = set([])
        ghosts = set([])
        cur.execute('SELECT name, type FROM files WHERE pkgKey=?', (uid,))
        for filename, ftype in cur:
            if ftype == 'file':
                files.add(filename)
            elif ftype == 'dir':
                dirs.add(filename)
            elif ftype == 'ghost':
                ghosts.add(filename)
        pp.files = files
        pp.dirs = dirs
        pp.ghosts = ghosts

        pri_obj.append(pp.checksum, pp)
    return pri_obj


def filelistsmetadata_from_sqlite_factory(sqlitepath, archpath):
    fil_obj = FilelistsMetadata(sqlitepath, archpath)

    con = sqlite.Connection(sqlitepath)
    fil_cur = con.cursor()
    fil_cur.execute('SELECT * FROM packages')
    for row in fil_cur:
        fp = FilelistsDbPackage()
        pkgkey = row[0]

        fp.checksum = row[1]

        cur = con.cursor()
        cur.execute('SELECT dirname, filenames, filetypes FROM filelist WHERE pkgKey=?',
                                                                    (pkgkey,))

        for dirname, filenames, filetypes in cur:
            # XXX: If there is dir without name '/' it's splited into 2 empty string
            #      so, if there are two empty string next to each other, replace
            #      it with only one empty string
            splited_filenames = filenames.split('/')
            filtered_splited_filenames = []
            if len(filenames):
                filtered_splited_filenames.append(splited_filenames[0])
            for i in xrange(1, len(filenames.split('/'))):
                if splited_filenames[i] == '' and splited_filenames[i-1] == '':
                    continue
                filtered_splited_filenames.append(splited_filenames[i])
            # XXX: End

            for filename, ftype in zip(filtered_splited_filenames, list(filetypes)):
                # If in XML is "foo" in db will be DIR: "." FILE: "foo"
                # Thus result will be "./foo" after join, so if dir is "."
                # do not do a join
                if dirname != ".":
                    path = os.path.join(dirname, filename)
                else:
                    path = filename

                if ftype == 'f':
                    fp.files.add(path)
                    fp.files_db.add(filename)
                elif ftype == 'd':
                    fp.dirs.add(path)
                    fp.dirs_db.add(filename)
                else:
                    fp.ghosts.add(path)
                    fp.ghosts_db.add(filename)
                fp.dbdirectories.append(dirname)
        fp.dbdirectories = sorted(fp.dbdirectories)
        fil_obj.append(fp.checksum, fp)
    return fil_obj


def othermetadata_from_sqlite_factory(sqlitepath, archpath):
    oth_obj = OtherMetadata(sqlitepath, archpath)

    con = sqlite.Connection(sqlitepath)
    oth_cur = con.cursor()
    oth_cur.execute('SELECT * FROM packages')
    for row in oth_cur:
        op = OtherPackage()
        pkgkey = row[0]

        op.checksum = row[1]

        cur = con.cursor()
        cur.execute('SELECT author, date, changelog FROM changelog WHERE pkgKey=? ORDER BY date ASC',
                                                                    (pkgkey,))

        for author, date, changelog in cur:
            op.changelogs.append((author, date, changelog))

        oth_obj.append(op.checksum, op)
    return oth_obj


#
# Repomd
#


def repomdmetadata_from_xml_factory(xmlpath):
    rm_obj = RepomdMetadata(xmlpath)

    for _, elements in etree.iterparse(xmlpath):
        elements = MyElement(elements)
        for elem in elements:
            elem = MyElement(elem)

            # Get revision
            if elem.tag.endswith("revision"):
                rm_obj.revision = elem.text

            # Parse tags
            if elem.tag.endswith("tags"):
                for subelem in elem:
                    if subelem.tag.endswith("content"):
                        rm_obj.tags.setdefault("content", set()).add(subelem.text)
                    if subelem.tag.endswith("repo"):
                        rm_obj.tags.setdefault("repo", set()).add(subelem.text)
                    if subelem.tag.endswith("distro"):
                        rm_obj.tags.setdefault("distro", set()).add((subelem.get("cpeid"),
                                                                     subelem.text))

    # Iter over data elements  (<data type="primary">, ...)
    for _, elements in etree.iterparse(xmlpath, tag="%sdata" % MD_NS):
        elements = MyElement(elements)
        re = RepomdItem()
        re.name = elements.get("type")
        for elem in elements:
            elem = MyElement(elem)
            if elem.tag.endswith("location"):
                re.location_href = elem.get("href")
            elif elem.tag.endswith("open-size"):
                re.open_size = elem.text
            elif elem.tag.endswith("open-checksum"):
                re.open_checksum_type = elem.get("type")
                re.open_checksum = elem.text
            elif elem.tag.endswith("checksum"):
                re.checksum_type = elem.get("type")
                re.checksum = elem.text
            elif elem.tag.endswith("timestamp"):
                re.timestamp = elem.text
            elif elem.tag.endswith("size"):
                re.size = elem.text

            elif elem.tag.endswith("database_version"):
                re.database_version = elem.text
        elements.clear()
        rm_obj.append(re.name, re)
    return rm_obj


#
# One repo
#


def xml_onerepo_factory(pri_path=None, fil_path=None,
                        oth_path=None, remove_tmp=True):
    # Check if all three repofiles (primary, filelists, other) exists
    if not pri_path:
        raise IOError("XML primary is missing %s" % pri_path)
    if not fil_path:
        raise IOError("XML filelists is missing %s" % fil_path)
    if not oth_path:
        raise IOError("XML other is missing %s" % oth_path)

    # Create tempdir
    tmpdir = tempfile.mkdtemp()
    new_pri_path = os.path.join(tmpdir, "primary.xml")
    new_fil_path = os.path.join(tmpdir, "filelists.xml")
    new_oth_path = os.path.join(tmpdir, "other.xml")

    # Bzip2 decompression
    if pri_path.endswith(".bz2"):
        open(new_pri_path, 'wb').write(bz2.BZ2File(pri_path, 'rb').read())
        open(new_fil_path, 'wb').write(bz2.BZ2File(fil_path, 'rb').read())
        open(new_oth_path, 'wb').write(bz2.BZ2File(oth_path, 'rb').read())
    # Gzip decompression
    elif pri_path.endswith(".gz"):
        open(new_pri_path, 'wb').write(gzip.open(pri_path, 'rb').read())
        open(new_fil_path, 'wb').write(gzip.open(fil_path, 'rb').read())
        open(new_oth_path, 'wb').write(gzip.open(oth_path, 'rb').read())
    # xz decompression
    elif pri_path.endswith(".xz"):
        open(new_pri_path, 'wb').write(liblzma.decompress(open(pri_path, 'rb').read()))
        open(new_fil_path, 'wb').write(liblzma.decompress(open(fil_path, 'rb').read()))
        open(new_oth_path, 'wb').write(liblzma.decompress(open(oth_path, 'rb').read()))

    # Read decompressed repo data
    pri = primarymetadata_from_xml_factory(new_pri_path, pri_path)
    fil = filelistsmetadata_from_xml_factory(new_fil_path, fil_path)
    oth = othermetadata_from_xml_factory(new_oth_path, oth_path)

    # Clean up
    if remove_tmp:
        shutil.rmtree(tmpdir)
        tmpdir = None
    return OneRepo(pri, fil, oth, tmpdir)


def xml_onerepo_from_path_factory(repopath, remove_tmp=True):
    pri_path = fil_path = oth_path = None
    for fname in os.listdir(repopath):
        if "primary.xml." in fname:
            pri_path = os.path.join(repopath, fname)
        elif "filelists.xml." in fname:
            fil_path = os.path.join(repopath, fname)
        elif "other.xml." in fname:
            oth_path = os.path.join(repopath, fname)
    return xml_onerepo_factory(pri_path, fil_path, oth_path, remove_tmp)


def sqlite_onerepo_factory(pri_path=None, fil_path=None,
                           oth_path=None, remove_tmp=True):
    # Check if all three repofiles (primary, filelists, other) exists
    if not pri_path or not fil_path or not oth_path:
        raise IOError("Some sqlite file are missing")

    # Create tempdir
    tmpdir = tempfile.mkdtemp()
    new_pri_path = os.path.join(tmpdir, "primary.sqlite")
    new_fil_path = os.path.join(tmpdir, "filelists.sqlite")
    new_oth_path = os.path.join(tmpdir, "other.sqlite")

    # Bzip2 uncompression
    if pri_path.endswith(".bz2"):
        open(new_pri_path, 'wb').write(bz2.BZ2File(pri_path, 'rb').read())
        open(new_fil_path, 'wb').write(bz2.BZ2File(fil_path, 'rb').read())
        open(new_oth_path, 'wb').write(bz2.BZ2File(oth_path, 'rb').read())
    # Gzip uncompression
    elif pri_path.endswith(".gz"):
        open(new_pri_path, 'wb').write(gzip.open(pri_path, 'rb').read())
        open(new_fil_path, 'wb').write(gzip.open(fil_path, 'rb').read())
        open(new_oth_path, 'wb').write(gzip.open(oth_path, 'rb').read())
    # xz decompression
    elif pri_path.endswith(".xz"):
        open(new_pri_path, 'wb').write(liblzma.decompress(open(pri_path, 'rb').read()))
        open(new_fil_path, 'wb').write(liblzma.decompress(open(fil_path, 'rb').read()))
        open(new_oth_path, 'wb').write(liblzma.decompress(open(oth_path, 'rb').read()))

    # Read decompressed repo data
    pri = primarymetadata_from_sqlite_factory(new_pri_path, pri_path)
    fil = filelistsmetadata_from_sqlite_factory(new_fil_path, fil_path)
    oth = othermetadata_from_sqlite_factory(new_oth_path, oth_path)

    # Clean up
    if remove_tmp:
        shutil.rmtree(tmpdir)
        tmpdir = None
    return OneRepo(pri, fil, oth, tmpdir)


def sqlite_onerepo_from_path_factory(repopath, remove_tmp=True):
    pri_path = fil_path = oth_path = None
    for fname in os.listdir(repopath):
        if "primary.sqlite." in fname:
            pri_path = os.path.join(repopath, fname)
        elif "filelists.sqlite." in fname:
            fil_path = os.path.join(repopath, fname)
        elif "other.sqlite." in fname:
            oth_path = os.path.join(repopath, fname)
    return sqlite_onerepo_factory(pri_path, fil_path, oth_path, remove_tmp)


#
# Complete repo
#


def completerepo_factory(repopath, sqliteauto=True, sqlite=False):
    # Load repomd.xml
    md = None
    md_path = os.path.join(repopath, "repodata/repomd.xml")
    if os.path.exists(md_path):
        md = repomdmetadata_from_xml_factory(md_path)
    else:
        print "Warning: repomd.xml is missing (%s)" % md_path

    # Load xml metadata (primary, filelists, other)
    if md:
        pri_path = fil_path = oth_path = None
        if md.get("primary") and md.get("primary").location_href:
            pri_path = os.path.join(repopath, md.get("primary").location_href)
        if md.get("filelists") and md.get("filelists").location_href:
            fil_path = os.path.join(repopath, md.get("filelists").location_href)
        if md.get("other") and md.get("other").location_href:
            oth_path = os.path.join(repopath, md.get("other").location_href)
        xmlrepo = xml_onerepo_factory(pri_path, fil_path, oth_path, remove_tmp=True)
    else:
        xmlrepo = xml_onerepo_from_path_factory(repopath, remove_tmp=True)

    # Load sqlite metadata (primary, filelists, other)
    sqlrepo = None
    if sqliteauto:
        pri = fil = oth = False
        for fname in os.listdir(repopath):
            if fname.endswith("primary.sqlite.bz2") or fname.endswith("primary.sqlite.gz") \
               or fname.endswith("primary.sqlite.xz"):
                pri = True
            if fname.endswith("filelists.sqlite.bz2") or fname.endswith("filelists.sqlite.gz") \
               or fname.endswith("filelists.sqlite.xz"):
                fil = True
            if fname.endswith("other.sqlite.bz2") or fname.endswith("other.sqlite.gz") \
               or fname.endswith("other.sqlite.xz"):
                oth = True
        if pri and fil and oth:
            sqlite = True

    if sqlite:
        if md:
            pri_path = fil_path = oth_path = None
            if md.get("primary_db") and md.get("primary_db").location_href:
                pri_path = os.path.join(repopath, md.get("primary_db").location_href)
            if md.get("filelists_db") and md.get("filelists_db").location_href:
                fil_path = os.path.join(repopath, md.get("filelists_db").location_href)
            if md.get("other_db") and md.get("other_db").location_href:
                oth_path = os.path.join(repopath, md.get("other_db").location_href)
            sqlite = sqlite_onerepo_factory(pri_path, fil_path, oth_path, remove_tmp=True)
        else:
            sqlite = sqlite_onerepo_from_path_factory(repopath, remove_tmp=True)

    return CompleteRepo(repopath, xmlrepo, sqlrepo, md)
