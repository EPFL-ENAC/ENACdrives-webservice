#!/usr/bin/env python3

# Bancal Samuel

# Tests conf.py


import io
import copy
import unittest
from utility import Output
from conf import read_config_source, validate_config


class TestReadConfigSource(unittest.TestCase):
    def test_empty(self):
        s_in = io.StringIO("")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(read_config_source(s_in), {})
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_comment(self):
        s_in = io.StringIO("""
# one two
[global]  # foo
Linux_CIFS_method = gvfs  # bar
# hello
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"global": {"Linux_CIFS_method": "gvfs"}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_unknown_section(self):
        s_in = io.StringIO("""
[glob]
Linux_CIFS_method = gvfs
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {}
            )
            s_out.seek(0)
            self.assertIn("Unexpected section", s_out.readlines()[0])

    def test_unknown_option(self):
        s_in = io.StringIO("""
[global]
Linux_CIFS_meth = gvfs
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {}
            )
            s_out.seek(0)
            self.assertIn("Unexpected option", s_out.readlines()[0])

    def test_bad_option(self):
        s_in = io.StringIO("""
[global]
name = test
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {}
            )
            s_out.seek(0)
            self.assertIn("Unexpected option", s_out.readlines()[0])

    def test_bad_servername(self):
        for s in ("'hello", "with_underscore", "&foo"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
server_name = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {}}}
                )
                s_out.seek(0)
                self.assertIn("server_name can only contain", s_out.readlines()[0])

    def test_path(self):
        s_in = io.StringIO(r"""
[CIFS_mount]
name = test
server_path = data\foo
local_path = \home\user\Desktop\mnt
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"CIFS_mount": {"test": {
                                 "server_path": "data/foo",
                                 "local_path": "/home/user/Desktop/mnt", }}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_bool_false(self):
        for s in ("non", "foobar", "false", "FALSE", "NO", "0"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
stared = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {
                                     "stared": False, }}}
                )
                s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_bool_true(self):
        for s in ("yes", "y", "true", "True", "TRUE", "1"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
Linux_gvfs_symlink = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {
                                     "Linux_gvfs_symlink": True, }}}
                )
                s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_cifs_mount_entry(self):
        s_in = io.StringIO(r"""
[CIFS_mount]
name = test
server_path = data\foo
local_path = \home\user\Desktop\mnt
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"CIFS_mount": {"test": {
                                 "server_path": "data/foo",
                                 "local_path": "/home/user/Desktop/mnt", }}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_config(self):
        s_in = io.StringIO(r"""
[global]
Linux_CIFS_method = gvfs
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = true

[realm]
name = EPFL
domain = INTRANET
username = bancal

[CIFS_mount]
name = private
label = bancal@files9
realm = EPFL
server_name = files9.epfl.ch
server_path = data/bancal
local_path = {MNT_DIR}/bancal_on_files9
#    {MNT_DIR}
#    {HOME_DIR}
#    {DESKTOP_DIR}
#    {LOCAL_USERNAME}
#    {LOCAL_GROUPNAME}
stared = false
#    default : False
Linux_CIFS_method = gvfs
#    mount.cifs : Linux's mount.cifs (requires sudo ability)
#    gvfs : Linux's gvfs-mount
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = yes
#    Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
#    default : True
Windows_letter = Z:
#    Drive letter to use for the mount
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {'CIFS_mount': {
                  'private': {
                   'Linux_CIFS_method': 'gvfs',
                   'Linux_gvfs_symlink': True,
                   'Linux_mountcifs_dirmode': '0770',
                   'Linux_mountcifs_filemode': '0770',
                   'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm',
                   'Windows_letter': 'Z:',
                   'label': 'bancal@files9',
                   'local_path': '{MNT_DIR}/bancal_on_files9',
                   'realm': 'EPFL',
                   'server_name': 'files9.epfl.ch',
                   'server_path': 'data/bancal',
                   'stared': False}},
                 'global': {
                  'Linux_CIFS_method': 'gvfs',
                  'Linux_gvfs_symlink': True,
                  'Linux_mountcifs_dirmode': '0770',
                  'Linux_mountcifs_filemode': '0770',
                  'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
                 'realm': {
                  'EPFL': {
                   'domain': 'INTRANET',
                   'username': 'bancal'}}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


class TestValidateConfig(unittest.TestCase):
    def test_empty(self):
        cfg = {}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), {})
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_basic_cifs_mount(self):
        cfg = {"CIFS_mount": {
                "name": {
                 "label": "label",
                 "realm": "r_name",
                 "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }},
               "realm": {
                "r_name": {
                 "username": "u",
                 "domain": "d", }}}
        cfg_expected = copy.deepcopy(cfg)
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_incomplete_cifs_mount(self):
        cfg = {"CIFS_mount": {
                "name": {
                 # "label": "label",
                 "realm": "realm",
                 "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }},
                "realm": {
                 "r_name": {
                  "username": "u",
                  "domain": "d", }}}
        cfg_expected = {"CIFS_mount": {}, 
                        "realm": {
                         "r_name": {
                          "username": "u",
                          "domain": "d", }}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertIn("expected 'label' option in CIFS_mount section.", s_out.readlines()[0])

    def test_missing_realm(self):
        cfg = {"CIFS_mount": {
                "name": {
                 "label": "label",
                 "realm": "r_name",
                 "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }}}
        cfg_expected = {"CIFS_mount": {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), ["Missing realm 'r_name'.\n", "Removing CIFS_mount 'name' repending on realm 'r_name'.\n"])


if __name__ == "__main__":
    unittest.main()