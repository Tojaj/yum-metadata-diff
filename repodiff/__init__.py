from repodiff.primary import PrimaryMetadata, PrimaryPackage
from repodiff.filelists import FilelistsMetadata, FilelistsPackage
from repodiff.other import OtherMetadata, OtherPackage
from repodiff.repo import OneRepo, CompleteRepo
from lxml import etree
import gzip
import bz2
import tempfile
import shutil
import os.path
try:
    import sqlite3 as sqlite
except ImportError:
    import sqlite

class XmlRepo(object):
    pass

class Repo(object):
    pass

# namespace
PRI_NS = "{http://linux.duke.edu/metadata/common}"
FIL_NS = "{http://linux.duke.edu/metadata/filelists}"
OTH_NS = "{http://linux.duke.edu/metadata/other}"

#
# XML
#

def _parse_pco(elem, requires=False):
    pco_dict = {}
    for felem in elem:
        if felem.tag.endswith("entry"):
            pco_dict[felem.get("name")] = (felem.get("flags"),
                felem.get("epoch"), felem.get("ver"), felem.get("rel"))
            if requires:
                pco_dict[felem.get("name")] += (bool(felem.get("pre")),)
    return pco_dict

def primarymetadata_from_xml_factory(xmlpath):
    pri_obj = PrimaryMetadata()
    for _, elements in etree.iterparse(open(xmlpath), tag="%spackage" % PRI_NS):
        pp = PrimaryPackage()
        for elem in elements:
            if elem.tag.endswith("name"):
                pp.name = elem.text
            elif elem.tag.endswith("arch"):
                pp.arch = elem.text
            elif elem.tag.endswith("version"):
                pp.epoch   = elem.get("epoch")
                pp.version = elem.get("ver")
                pp.release = elem.get("rel")
            elif elem.tag.endswith("checksum"):
                pp.checksum_type = elem.get("type")
                pp.checksum      = elem.text
            elif elem.tag.endswith("summary"):
                pp.summary = elem.text
            elif elem.tag.endswith("description"):
                pp.description = elem.text
            elif elem.tag.endswith("packager"):
                pp.packager = elem.text
            elif elem.tag.endswith("url"):
                pp.url = elem.text
            elif elem.tag.endswith("time"):
                pp.time_file  = int(elem.get("file"))
                pp.time_build = int(elem.get("build"))
            elif elem.tag.endswith("size"):
                pp.size_package   = int(elem.get("package"))
                pp.size_installed = int(elem.get("installed"))
                pp.size_archive   = int(elem.get("archive"))
            elif elem.tag.endswith("location"):
                pp.location = elem.get("href")
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
        pri_obj.append(pp)
    return pri_obj


def filelistsmetadata_from_xml_factory(xmlpath):
    fil_obj = FilelistsMetadata()
    for _, elements in etree.iterparse(open(xmlpath), tag="%spackage" % FIL_NS):
        fp = FilelistsPackage()
        fp.checksum = elements.get("pkgid")
        fp.arch     = elements.get("arch")
        fp.name     = elements.get("name")
        for elem in elements:
            if elem.tag.endswith("version"):
                fp.epoch   = elem.get("epoch")
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
        fil_obj.append(fp)
    return fil_obj


def othermetadata_from_xml_factory(xmlpath):
    oth_obj = OtherMetadata()
    for _, elements in etree.iterparse(open(xmlpath), tag="%spackage" % OTH_NS):
        op = OtherPackage()
        op.checksum = elements.get("pkgid")
        op.arch     = elements.get("arch")
        op.name     = elements.get("name")
        for elem in elements:
            if elem.tag.endswith("version"):
                op.epoch   = elem.get("epoch")
                op.version = elem.get("ver")
                op.release = elem.get("rel")
            elif elem.tag.endswith("changelog"):
                op.changelogs.append((elem.get("author"), int(elem.get("date")), elem.text))
        elements.clear()
        oth_obj.append(op)
    return oth_obj

#
# Sqlite
#

def primarymetadata_from_sqlite_factory(sqlitepath):
    pri_obj = PrimaryMetadata()

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
            pco_dict = {}
            cur.execute('SELECT * FROM %s WHERE pkgKey=?' % pco, (uid,))
            for name, flag, epoch, ver, rel, _ in cur:
                pco_dict[name] = (flag, epoch, ver, rel)
            setattr(pp, pco, pco_dict)

        # requires
        req_dict = {}
        cur.execute('SELECT * FROM requires WHERE pkgKey=?', (uid,))
        for name, flag, epoch, ver, rel, _, pre in cur:
            if pre == 'TRUE':
                pre = 1
            else:
                pre = 0
            req_dict[name] = (flag, epoch, ver, rel, pre)
        setattr(pp, 'requires', req_dict)

        #files
        files  = set([])
        dirs   = set([])
        ghosts = set([])
        cur.execute('SELECT name, type FROM files WHERE pkgKey=?', (uid,))
        for filename, ftype in cur:
            if ftype == 'file':
                files.add(filename)
            elif ftype == 'dir':
                dirs.add(filename)
            elif ftype == 'ghosts':
                ghosts.add(filename)
        pp.files   = files
        pp.dirs    = dirs
        pp.ghostst = ghosts

        pri_obj.append(pp)
    return pri_obj


def filelistsmetadata_from_sqlite_factory(sqlitepath):
    fil_obj = FilelistsMetadata()

    con = sqlite.Connection(sqlitepath)
    fil_cur = con.cursor()
    fil_cur.execute('SELECT * FROM packages')
    for row in fil_cur:
        fp = FilelistsPackage()
        pkgkey = row[0]

        fp.checksum = row[1]

        cur = con.cursor()
        cur.execute('SELECT dirname, filenames, filetypes FROM filelist WHERE pkgKey=?',
                                                                    (pkgkey,))

        for dirname, filenames, filetypes in cur:
            for filename, ftype in zip(filenames.split('/'), list(filetypes)):
                path = os.path.join(dirname, filename)
                if ftype == 'f':
                    fp.files.add(path)
                elif ftype == 'd':
                    fp.dirs.add(path)
                else:
                    fp.ghosts.add(path)
        fil_obj.append(fp)
    return fil_obj


def othermetadata_from_sqlite_factory(sqlitepath):
    oth_obj = OtherMetadata()

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

        oth_obj.append(op)
    return oth_obj


#
# One repo
#

def xml_onerepo_factory(repopath):
    pri_path = os.path.join(repopath, "primary.xml.gz")
    fil_path = os.path.join(repopath, "filelists.xml.gz")
    oth_path = os.path.join(repopath, "other.xml.gz")

    # Check if all three repofiles (primary, filelists, other) exists
    for filename in (pri_path, fil_path, oth_path):
        if not os.path.exists(filename):
            raise IOError("File '%s' doesn't exist" % filename)

    # Create tempdir
    tmpdir = tempfile.mkdtemp()
    new_pri_path = os.path.join(tmpdir, "primary.xml")
    new_fil_path = os.path.join(tmpdir, "filelists.xml")
    new_oth_path = os.path.join(tmpdir, "other.xml")

    # Gzip decompression
    open(new_pri_path, 'wb').write(gzip.open(pri_path, 'rb').read())
    open(new_fil_path, 'wb').write(gzip.open(fil_path, 'rb').read())
    open(new_oth_path, 'wb').write(gzip.open(oth_path, 'rb').read())

    # Read decompressed repo data
    pri = primarymetadata_from_xml_factory(new_pri_path)
    fil = filelistsmetadata_from_xml_factory(new_fil_path)
    oth = othermetadata_from_xml_factory(new_oth_path)

    # Clean up
    shutil.rmtree(tmpdir)
    return OneRepo(pri, fil, oth)


def sqlite_onerepo_factory(repopath):
    pri_path = os.path.join(repopath, "primary.sqlite.bz2")
    fil_path = os.path.join(repopath, "filelists.sqlite.bz2")
    oth_path = os.path.join(repopath, "other.sqlite.bz2")

    # Check if all three repofiles (primary, filelists, other) exists
    for filename in (pri_path, fil_path, oth_path):
        if not os.path.exists(filename):
            raise IOError("File '%s' doesn't exist" % filename)

    # Create tempdir
    tmpdir = tempfile.mkdtemp()
    new_pri_path = os.path.join(tmpdir, "primary.sqlite")
    new_fil_path = os.path.join(tmpdir, "filelists.sqlite")
    new_oth_path = os.path.join(tmpdir, "other.sqlite")

    # Bzip2 decompression
    open(new_pri_path, 'wb').write(bz2.BZ2File(pri_path, 'rb').read())
    open(new_fil_path, 'wb').write(bz2.BZ2File(fil_path, 'rb').read())
    open(new_oth_path, 'wb').write(bz2.BZ2File(oth_path, 'rb').read())

    # Read decompressed repo data
    pri = primarymetadata_from_sqlite_factory(new_pri_path)
    fil = filelistsmetadata_from_sqlite_factory(new_fil_path)
    oth = othermetadata_from_sqlite_factory(new_oth_path)

    # Clean up
    shutil.rmtree(tmpdir)
    return OneRepo(pri, fil, oth)


#
# Complete repo
#

def completerepo_factory(repopath, sqliteauto=True, sqlite=False):
    xmlrepo = xml_onerepo_factory(repopath)
    sqlrepo = None
    if sqlite:
        sqlrepo = sqlite_onerepo_factory(repopath)
    elif sqliteauto:
        pri_path = os.path.join(repopath, "primary.sqlite.bz2")
        fil_path = os.path.join(repopath, "filelists.sqlite.bz2")
        oth_path = os.path.join(repopath, "other.sqlite.bz2")
        if os.path.exists(pri_path) and \
           os.path.exists(fil_path) and \
           os.path.exists(oth_path):
            sqlrepo = sqlite_onerepo_factory(repopath)
    return CompleteRepo(xmlrepo, sqlrepo)
