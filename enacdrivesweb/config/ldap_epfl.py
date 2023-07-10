import re
import ldap3


class UserNotFoundException(Exception):
    pass


class Ldap:
    """
    EPFL Ldap connector
    """

    def __init__(self):
        self.server_name = "ldap.epfl.ch"
        self.server = ldap3.Server(self.server_name)
        self.conn = ldap3.Connection(
            self.server, client_strategy=ldap3.SAFE_SYNC, auto_bind=True
        )
        self.scope = "SUBTREE"

    def read_ldap(self, l_filter, l_attrs, base_dn="o=epfl,c=ch"):
        """
        + Proceed a request to the LDAP
        + sort entries (only possible if "uid" attribute was requested)
            + 1st is main accreditation
            + other accreditations come after, unsorted
        """
        if not self.conn.bound:
            raise Exception("Could not bind to {}".format(self.server_name))
        _, _, response, _ = self.conn.search(
            search_base=base_dn,
            search_filter=l_filter,
            search_scope=self.scope,
            attributes=l_attrs,
        )

        if response is None:
            return []

        # Return main accreditation first.
        # + main's uid attribute has 2 values : "username", "username@unit"
        # + other's uid attribute has 1 value : "username@unit"
        return sorted(
            response, key=lambda e: len(e["attributes"].get("uid", [])), reverse=True
        )


def get_user_settings(username):
    """
    1) Search ldap.epfl.ch for that username
        -> uniqueIdentifier
    2) Search ldap.epfl.ch for that uniqueIdentifier
        -> epfl_units (third "ou=xxx" of dn)
        -> ldap_groups
    returns {
                "auth_domain": "INTRANET",
                "displayName": None,
                "sciper": None,
                "last_sciper_digit": None,
                "epfl_units": [],
                "ldap_groups": [],
            }
    """
    l = Ldap()
    user_settings = {
        "username": username,
        "auth_domain": "INTRANET",
        "displayName": None,
        "sciper": None,
        "last_sciper_digit": None,
        "epfl_units": [],
        "ldap_groups": [],
    }

    # A) Look for his/her uniqueIdentifier (#SCIPER)
    # -> displayName
    # -> sciper
    # -> last_sciper_digit
    r = l.read_ldap(
        "(uid={0})".format(username),
        [
            "uniqueIdentifier",
            "displayName",
        ],
        "c=ch",
    )
    if len(r) == 0:
        # debug_logger.debug("get_user_settings({}) : UserNotFoundException".format(username))
        raise UserNotFoundException(username)
    sciper_no = r[0]["attributes"]["uniqueIdentifier"][0]
    user_settings["displayName"] = r[0]["attributes"]["displayName"][0]
    user_settings["sciper"] = sciper_no
    user_settings["last_sciper_digit"] = sciper_no[-1]

    # B) Look for all his/her accreditations
    # -> epfl_units sorted as :
    #    #1 is main accred
    #    #2++ are alphabeticaly sorted
    # -> ldap_groups sorted alphabeticaly
    user_settings["epfl_units"] = []
    ldap_groups = set()
    r = l.read_ldap(
        "(uniqueIdentifier={0})".format(sciper_no),
        [
            "uid",
            "memberOf",
        ],
    )
    for accred in r:
        all_ou = re.findall(r"ou=([^,]+)", accred["dn"])
        if len(all_ou) >= 3:
            user_settings["epfl_units"].append(all_ou[-3])
        try:
            ldap_groups = ldap_groups.union(accred["attributes"]["memberOf"])
        except KeyError:
            pass
    user_settings["epfl_units"] = user_settings["epfl_units"][:1] + sorted(
        user_settings["epfl_units"][1:]
    )
    user_settings["ldap_groups"] = sorted(list(ldap_groups))

    return user_settings
