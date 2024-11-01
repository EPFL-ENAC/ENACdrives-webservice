import os
import re
import subprocess
from django.utils.encoding import smart_str

from config import models as mo
from enacdrivesweb import settings


def validate_input(data_source, data_type):
    """
    Validates data received from HTTP requests
    """
    if data_type == "username":
        data = data_source(data_type, "")
        data = smart_str(data, errors="ignore")
        data = data.lower()
        all_str = re.findall(r"\w", data)
        # all_str = re.findall(r"[\w\.@]", data) # needed for username=a.s.bancal@bluewin.ch (test)
        data = "".join(all_str)
        return data
    elif data_type in ("version", "os", "os_version"):
        data = data_source(data_type, "")
        data = smart_str(data, errors="ignore")
        return data
    raise Exception("Unknown data_type '{0}'".format(data_type))


def grep_mount_names(config_str):
    """
    Parse config_str and return every *_mount names
    """
    save_name = False
    names = []
    for l in config_str.split("\n"):
        l = l.strip()
        if l.startswith("[CIFS_mount]"):
            save_name = True
            continue

        try:
            k, v = re.match(r"([^=]*)=(.*)", l).groups()
            k, v = k.strip(), v.strip()
        except AttributeError:
            continue
        if save_name and k == "name":
            names.append(v)
            save_name = False

    return names


def conf_filter(data, iteration_num):
    """
    will replace lines like
    0.Windows_letter = Y:
    1.Windows_letter = X:
    2.Windows_letter = W:

    to "Windows_letter = Y:" when iteration_num == 0
    to "Windows_letter = X:" when iteration_num == 1
    to "Windows_letter = W:" when iteration_num == 2
    to nothing otherwise

    Other example with "*" :
    0.Windows_letter = Y:
    *.Windows_letter = X:

    to "Windows_letter = Y:" when iteration_num == 0
    to "Windows_letter = X:" otherwise (which is not a good idea of course)
    """
    # debug_logger = logging.getLogger("debug")
    iteration_num = str(iteration_num)

    def close_section(special_lines, result):
        # debug_logger.debug("close.{} : {}".format(iteration_num, special_lines))
        if len(special_lines) == 0:
            return
        for k in special_lines:
            if iteration_num in special_lines[k]:
                result.append(special_lines[k][iteration_num])
            elif "*" in special_lines[k]:
                result.append(special_lines[k]["*"])
        result.append("")

    lines = data.split("\n")
    special_lines = {}
    result = []
    for l in lines:
        l = l.strip()
        if l == "":
            continue
        if l.startswith("["):
            close_section(special_lines, result)
            special_lines = {}
        m = re.match(r"([\d*]*)\.(([^=]*)=.*)$", l)
        if m:
            i = m.group(1).strip()
            k = m.group(3).strip()
            v = m.group(2).strip()
            # debug_logger.debug("found {} . {} . {}".format(i, k, v))
            special_lines.setdefault(k, {})
            special_lines[k][i] = v
        else:
            result.append(l)
    close_section(special_lines, result)

    return "\n".join(result)


def split_filter(st):
    """
    split filter into 2 elements :
    + operator (=|<|<=|>|>=)
    + string to be checked
    """
    m = re.match(r"^ *([=<>]+)? *['\"]?([^'\"]*)['\"]?$", st)
    if m:
        return m.groups()
    else:
        raise Exception("Unrecognized filter '{}' (1)".format(st))


def get_list_versions(filter_version, version):
    """
    transform string into list of int for both filter_version and version
    adapt length of verion's list to match length of filter.
    """
    l_filter_version = [int(s) for s in re.findall(r"\d+", filter_version)]
    l_version = [int(s) for s in re.findall(r"\d+", version)]
    for i in range(len(l_filter_version) - len(l_version)):
        l_version.append(0)
    for i in range(len(l_version) - len(l_filter_version)):
        l_version.pop()
    return l_filter_version, l_version


def compare_versions(the_filter, value):
    """
    compare version from value with the_filter
    """
    op_filter, st_filter = split_filter(the_filter)
    if op_filter is None:
        return st_filter == value
    else:
        l_filter, l_value = get_list_versions(st_filter, value)
        if op_filter == "=":
            for i in range(len(l_filter)):
                # Only browse the number of digit specified by the filter (10.10 will match 10.10.2 for instance)
                if l_value[i] != l_filter[i]:
                    return False
            return True
        if op_filter == "<":
            smaller = False
            for i in range(len(l_filter)):
                if l_value[i] < l_filter[i]:
                    smaller = True
                    break
                elif l_value[i] > l_filter[i]:
                    smaller = False
                    break
            return smaller
        if op_filter == "<=":
            smaller_equal = True
            for i in range(len(l_filter)):
                if l_value[i] < l_filter[i]:
                    smaller_equal = True
                    break
                elif l_value[i] > l_filter[i]:
                    smaller_equal = False
                    break
            return smaller_equal
        if op_filter == ">":
            greater = False
            for i in range(len(l_filter)):
                if l_value[i] > l_filter[i]:
                    greater = True
                    break
                elif l_value[i] < l_filter[i]:
                    greater = False
                    break
            return greater
        if op_filter == ">=":
            greater_equal = True
            for i in range(len(l_filter)):
                if l_value[i] > l_filter[i]:
                    greater_equal = True
                    break
                elif l_value[i] < l_filter[i]:
                    greater_equal = False
                    break
            return greater_equal
        else:
            raise Exception("Unrecognized filter '{}' (2)".format(the_filter))


def client_filter(conf, request):
    """
    return True if that conf is to be included for that client
    based on client_filter_os, client_filter_os_version and client_filter_version
    """

    if conf.client_filter_os != "":
        op, st = split_filter(conf.client_filter_os)
        client_os = validate_input(request.GET.get, "os")
        if not client_os == st:
            return False
    if conf.client_filter_os_version != "":
        client_os_version = validate_input(request.GET.get, "os_version")
        if not compare_versions(conf.client_filter_os_version, client_os_version):
            return False
    if conf.client_filter_version != "":
        client_version = validate_input(request.GET.get, "version")
        if not compare_versions(conf.client_filter_version, client_version):
            return False

    return True


def is_client_in_minimal_releases(minimal_releases, request):
    """
    return True if the client's version matches minimal_releases expected
    """
    client_os = validate_input(request.GET.get, "os")
    client_version = validate_input(request.GET.get, "version")
    if client_os in minimal_releases:
        if not compare_versions(minimal_releases[client_os], client_version):
            return False
    return True


def remove_all_mount(original_config):
    """
    return config_given as original_config, without all [CIFS_mount] entries
    useful for clients that are not supported anymore.
    """
    config_given = ""
    current_section = ""
    for line in original_config.split("\n"):
        m = re.match(r"^\[(.*)\]", line)
        if m:
            current_section = m.group(1).lower()
        if current_section != "cifs_mount":
            config_given += line + "\n"
    return config_given


def check_config():
    CIFS_UNIT_CONFIG = (
        {
            "server": "enac1files.epfl.ch",
            "config name": "NAS3 Files",
            "shares_to_ignore": (
                r".*\$$",  # all shares finished by a "$"
                r"academic-alpole",
                r"antfr-ge",
                r"biomining",
                r"camipro-2018",
                r"digiwalls-ibois-eesd",
                r"dropim",
                r"ecombine",
                r"enac-prom-acad",
                r"geome",
                r"gestion-unites-enac",
                r"icarus",
                r"infra-sculpture",
                r"ivea",
                r"lablysi",
                r"phlebicite",
                r"proj-.*$",  # all proj- shares
                r"s_pine",
                r"sar-web",
                r"si_topsolid_debug_files",
                r"technologie_du_bati_2",
                r"technologie_du_bati_4",
                r"uhna",
                r"vaertical",
                r"wanhabitats",
            ),
            "units_to_ignore": (),
        },
        {
            "server": "enac1arch.epfl.ch",
            "config name": "NAS3 Arch",
            "shares_to_ignore": (
                r".*\$$",  # all shares finished by a "$"
                r"enac-webcom",
                r"geome",
                r"oldlabs",
                r"sar-winprofiles",
                r"sgc-winprofiles",
                r"ssie-salles",
            ),
            "units_to_ignore": (),
        },
        {
            "server": "enac2raw.epfl.ch",
            "config name": "NAS3 Raw2",
            "shares_to_ignore": (r".*\$$",),  # all shares finished by a "$"
            "units_to_ignore": (),
        },
    )
    CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, "enacmoni.cred")

    def list_smb_shares(cfg):
        shares = []
        cmd = ["smbclient", "-A", CREDENTIALS_FILE, "-L", cfg["server"], "-m", "SMB3"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

        # parse output
        for line in output.split("\n"):
            match = re.match(r"\s*(\S+)\s+Disk\s.*$", line)
            if match:
                valid_share = True
                share = match.group(1).lower()
                for filter_out in cfg["shares_to_ignore"]:
                    if re.match(filter_out, share):
                        valid_share = False
                if valid_share:
                    shares.append(share)

        return set(shares)

    status = 0
    output = ""
    for cfg in CIFS_UNIT_CONFIG:
        output += f"Checking {cfg['config name']}: \n"
        shares = list_smb_shares(cfg)
        cfg["shares"] = shares
        c = mo.Config.objects.get(name=cfg["config name"])
        c_units = set([u.name.lower() for u in c.epfl_units.all()])

        missing = shares - c_units
        too_much = c_units - shares
        if len(missing) != 0:
            output += f"Error. Missing units: {list(missing)}\n"
            status = 2
        if len(too_much) != 0:
            output += f"Error. Too much units: {list(too_much)}\n"
            status = 2
        if len(missing) + len(too_much) == 0:
            output += "Units for this filer are correctly configured.\n"

    output += f"exit with {status=}\n"
    return (status, output)
