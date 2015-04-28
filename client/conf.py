#!/usr/bin/env python3

# Bancal Samuel

# Offers get_config() which
#  + parse config from
#    + default values (hard coded in source)
#    + http://enacdrives.epfl.ch/config?username=xxx
#    + System's config
#    + User's config
#  + merge them
#  + validate

import os
import re
import io
import pprint
import hashlib
import urllib.error
import urllib.request
from utility import Output, CONST


FileNotFoundException = getattr(__builtins__, 'FileNotFoundError', IOError)


class ConfigException(Exception):
    pass


def get_config():
    # Create cache_dir if not already existent
    if not os.path.exists(CONST.USER_CACHE_DIR):
        os.makedirs(CONST.USER_CACHE_DIR)

    # HARD CODED CONFIG
    default_config = {
        'global': {
         'Linux_CIFS_method': 'gvfs',
         'Linux_gvfs_symlink': True,
         'Linux_mountcifs_dirmode': '0770',
         'Linux_mountcifs_filemode': '0770',
         'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
        }
    cfg = default_config
    
    # USER CONFIG -> get only username from [global]
    user_config = None
    username = None
    try:
        with open(CONST.USER_CONF_FILE, "r") as f:
            user_config = read_config_source(f)
        username = user_config.get("global", {}).get("username", None)
        if username is not None:
            Output.write("Loaded username '{}' from User context. ({})".format(username, CONST.USER_CONF_FILE))
        else:
            Output.write("Username not found in User context. ({})".format(CONST.USER_CONF_FILE))
    except FileNotFoundException:
        Output.write("Username not found in User context. ({})".format(CONST.USER_CONF_FILE))

    # ENACDRIVE SERVER CONFIG (included cache function)
    if username is not None:
        config_url = CONST.CONFIG_URL.format(username=username)
        cache_filename = os.path.join(CONST.USER_CACHE_DIR, hashlib.md5(config_url.encode()).hexdigest())
        try:
            with urllib.request.urlopen(config_url) as response:
                lines = [l.decode() for l in response.readlines()]
                s_io = io.StringIO("".join(lines))
                enacdrives_config = read_config_source(s_io)
                merge_configs(cfg, enacdrives_config)
                s_io.seek(0)
                with open(cache_filename, "w") as f:
                    f.writelines(s_io.readlines())
            Output.write("Loaded config from ENACdrives server ({})".format(config_url))
        except urllib.error.URLError:
            Output.write("Warning, could not load config ENACdrives server. ({})".format(config_url))
            try:
                with open(cache_filename, "r") as f:
                    cached_config = read_config_source(f)
                    merge_configs(cfg, cached_config)
                Output.write("Loaded config from cache file. ({})".format(cache_filename))
            except FileNotFoundException:
                Output.write("!!! Error, could not load config from cache file. ({})".format(cache_filename))
    else:
        Output.write("Skipping config from ENACdrives server (no username).")

    # SYSTEM CONFIG
    try:
        with open(CONST.SYSTEM_CONF_FILE, "r") as f:
            system_config = read_config_source(f)
            merge_configs(cfg, system_config)
        Output.write("Loaded config from System context. ({})".format(CONST.SYSTEM_CONF_FILE))
    except FileNotFoundException:
        Output.write("No config found from System context. ({})".format(CONST.SYSTEM_CONF_FILE))
    
    # USER CONFIG
    if user_config is not None:
        merge_configs(cfg, user_config)
        Output.write("Loaded config from User context. ({})".format(CONST.USER_CONF_FILE))
    else:
        Output.write("No config found from User context. ({})".format(CONST.USER_CONF_FILE))
    
    cfg = validate_config(cfg)
    return cfg


def save_username(username):
    lines = ["", ]
    try:
        user_config = None
        with open(CONST.USER_CONF_FILE, "r") as f:
            lines = f.readlines()
            
        # Parse file, search for username = xxx in [global]
        current_section = None
        line_nb = -1
        global_section_line_nb = None
        username_line_nb = None
        for l in lines:
            line_nb += 1
            if l.startswith("["):
                try:
                    current_section = re.match(r"\[(\S+)\]$", l).groups()[0]
                    if current_section == "global" and global_section_line_nb is None:
                        global_section_line_nb = line_nb
                except AttributeError:
                    current_section = None
                continue
            if current_section != "global":
                continue
            try:
                k, v = re.match(r"([^=]*)=(.*)", l).groups()
                k, v = k.strip(), v.strip()
            except AttributeError:
                continue
            if k == "username":
                username_line_nb = line_nb
                break
        
        # username found in config file
        if username_line_nb is not None:
            Output.write("Changing to username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines[username_line_nb] = "username = {}\n".format(username)
        
        # username not found, but [global] found
        elif global_section_line_nb is not None:
            Output.write("Saving username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines.insert(global_section_line_nb+1, "username = {}\n".format(username))
        
        # username not found, [global] not found
        else:
            Output.write("Saving username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines.insert(0, "[global]\n")
            lines.insert(1, "username = {}\n".format(username))
        
    except FileNotFoundException:
        Output.write("Saving username='{}' to new config file {}".format(username, CONST.USER_CONF_FILE))
        lines.insert(0, "[global]\n")
        lines.insert(1, "username = {}\n".format(username))
    
    with open(CONST.USER_CONF_FILE, "w") as f:
        f.writelines(lines)
    
    
def merge_configs(cfg, cfg_to_merge):
    cfg.setdefault("global", {})
    
    # merge entries_order (priority to cfg_to_merge, then add missing from cfg)
    cfg_to_merge.setdefault("global", {})
    cfg_to_merge["global"].setdefault("entries_order", [])
    for entry in cfg["global"].get("entries_order", []):
        if entry not in cfg_to_merge["global"]["entries_order"]:
            cfg_to_merge["global"]["entries_order"].append(entry)
            
    # merge ["global"]
    cfg["global"].update(cfg_to_merge.get("global", {}))
    
    # merge ["CIFS_mount"]
    cfg.setdefault("CIFS_mount", {})
    for cifs_m in cfg_to_merge.get("CIFS_mount", {}):
        cfg["CIFS_mount"].setdefault(cifs_m, {})
        cfg["CIFS_mount"][cifs_m].update(cfg_to_merge["CIFS_mount"][cifs_m])
    
    # merge ["realm"]
    cfg.setdefault("realm", {})
    for realm in cfg_to_merge.get("realm", {}):
        cfg["realm"].setdefault(realm, {})
        cfg["realm"][realm].update(cfg_to_merge["realm"][realm])
    
    return cfg


def validate_value(option, value):
    if option == "Linux_CIFS_method":
        if value not in ("gvfs", "mount.cifs"):
            raise ConfigException("Error, Linux_CIFS_method has to be 'gvfs' or 'mount.cifs'.")
    elif option == "entries_order":
        value = [e.strip() for e in value.split(",")]
    elif option in ("server_path", "local_path"):
        value = re.sub(r"\\", "/", value)
    elif option == "domain":
        value = value.upper()
    elif option == "username":
        value = value.lower()
    elif option == "server_name":
        if bool(re.search(r"[^a-zA-Z0-9.-]", value)):
            raise ConfigException("Error, server_name can only contain alphanumeric, and '-' and '.' symbols.")
    elif option in ("stared", "Linux_gvfs_symlink"):
        value = str(value).lower()
        return value in ("yes", "y", "true", "1", "on")
    elif option == "Windows_letter":
        value = value.upper()
        if not re.match(r"[A-Z]:$", value):
            raise ConfigException("Error, Windows drive letter has to be on the form 'Z:'.")
    return value


def read_config_source(src):
    """
        Readlines on src
            [global]
            username = bancal
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

        And return cfg as
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
              'username': 'bancal',
              'Linux_CIFS_method': 'gvfs',
              'Linux_gvfs_symlink': True,
              'Linux_mountcifs_dirmode': '0770',
              'Linux_mountcifs_filemode': '0770',
              'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
             'realm': {
              'EPFL': {
               'domain': 'INTRANET',
               'username': 'bancal'}}}
    """
    
    def save_current_section():
        try:
            name = current_section_values["name"]
            del(current_section_values["name"])
            cfg.setdefault(current_section_name, {})
            cfg[current_section_name].setdefault(name, {})
            cfg[current_section_name][name].update(current_section_values)
        except KeyError:
            Output.write("Error : Expected name option not found in at line {}. Skipping that section.".format(section_line_nb))
    
    multi_entries_sections = ("CIFS_mount", "realm")
    allowed_options = {
        "global": (
            "username",
            "entries_order",
            "Linux_CIFS_method",
            "Linux_mountcifs_filemode",
            "Linux_mountcifs_dirmode",
            "Linux_mountcifs_options",
            "Linux_gvfs_symlink",
        ),
        "CIFS_mount": (
            "name",
            "label",
            "realm",
            "server_name",
            "server_path",
            "local_path",
            "stared",
            "Linux_CIFS_method",
            "Linux_mountcifs_filemode",
            "Linux_mountcifs_dirmode",
            "Linux_mountcifs_options",
            "Linux_gvfs_symlink",
            "Windows_letter",
        ),
        "realm": (
            "name",
            "domain",
            "username",
        ),
    }
    
    cfg = {}
    current_section_name = ""
    current_section_values = {}
    line_nb = 0
    section_line_nb = 0
    for line in src.readlines():
        if type(line) == bytes:
            line = line.decode()
        line_nb += 1
        l = line
        l = re.sub(r"#.*", "", l)  # remove comments
        l = l.strip()  # remove white spaces
        if l == "":
            continue
        # Output.write(l)
        
        # New section
        if l.startswith("["):
            try:
                new_section = re.match(r"\[(\S+)\]$", l).groups()[0]
            except AttributeError:
                Output.write("Error : Unexpected content at line {}:\n{}".format(line_nb, line))
                continue
            if current_section_name in multi_entries_sections and current_section_values != {}:
                # Save previous section content
                save_current_section()
            if new_section in allowed_options:
                current_section_name = new_section
                current_section_values = {}
                section_line_nb = line_nb
            else:
                Output.write("Error : Unexpected section name '{}' at line {}:\n{}".format(new_section, line_nb, line))
                current_section_name = ""
            continue
        
        if current_section_name == "":
            Output.write("Error : Unexpected content at line {}:\n{}".format(line_nb, line))
            continue
        
        # New option
        try:
            k, v = re.match(r"([^=]*)=(.*)", l).groups()
            k, v = k.strip(), v.strip()
        except AttributeError:
            continue
        if k not in allowed_options[current_section_name]:
            Output.write("Error : Unexpected option at line {}:\n{}".format(line_nb, line))
            continue
        
        try:
            if current_section_name in multi_entries_sections:
                # This is a multi entries section type
                current_section_values[k] = validate_value(k, v)
            else:
                # This is a single entry section type
                cfg.setdefault(current_section_name, {})[k] = validate_value(k, v)
        except ConfigException as e:
            Output.write(str(e))
            
        # Output.write("'{}' = '{}'".format(k, v))
    
    if current_section_name in multi_entries_sections and current_section_values != {}:
        # Save last section content
        save_current_section()
    
    return cfg


def validate_config(cfg):
    """
    Validates that there is everything necessary in the config to do the job.
    Will output error message otherwise
    """
    
    def expect_option(entry, section, option):
        if option not in entry:
            Output.write("Error: expected '{}' option in {} section.".format(option, section))
            return False
        return True

    invalid_cifs_m = []
    invalid_realm = []
    expected_realms = {}
    for m_name in cfg.get("CIFS_mount", {}):
        is_ok = (
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "label") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "realm") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "server_name") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "server_path") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "local_path")
        )
        if is_ok:
            realm = cfg["CIFS_mount"][m_name]["realm"]
            expected_realms.setdefault(realm, [])
            expected_realms[realm].append(m_name)
        else:
            Output.write("Removing incomplete CIFS_mount '{}'.".format(m_name))
            invalid_cifs_m.append(m_name)
    
    for realm in expected_realms:
        if realm not in cfg.get("realm", []):
            Output.write("Missing realm '{}'.".format(realm))
            for m_name in expected_realms[realm]:
                Output.write("Removing CIFS_mount '{}' depending on realm '{}'.".format(m_name, realm))
                invalid_cifs_m.append(m_name)

    for realm in cfg.get("realm", []):
        is_ok = (
            expect_option(cfg["realm"][realm], "realm", "username") and
            expect_option(cfg["realm"][realm], "realm", "domain")
        )
        if not is_ok:
            Output.write("Removing incomplete realm '{}'.".format(realm))
            invalid_realm.append(realm)
            for m_name in expected_realms.get(realm, []):
                Output.write("Removing CIFS_mount '{}' depending on realm '{}'.".format(m_name, realm))
                invalid_cifs_m.append(m_name)

    for m_name in invalid_cifs_m:
        del(cfg["CIFS_mount"][m_name])

    for realm in invalid_realm:
        del(cfg["realm"][realm])
    
    return cfg


def main():
    with Output():
        cfg = get_config()
        Output.write(pprint.pformat(cfg))

if __name__ == "__main__":
    main()
