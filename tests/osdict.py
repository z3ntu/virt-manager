# Copyright (C) 2013 Red Hat, Inc.
#
# This work is licensed under the GNU GPLv2 or later.
# See the COPYING file in the top-level directory.

import unittest

from virtinst import OSDB

from tests import utils


class TestOSDB(unittest.TestCase):
    """
    Test osdict/OSDB
    """
    def test_osdict_aliases_ro(self):
        aliases = getattr(OSDB, "_aliases")

        if len(aliases) != 42:
            raise AssertionError(_("OSDB._aliases changed size. It "
                "should never be extended, since it is only for back "
                "compat with pre-libosinfo osdict.py"))

    def test_osdict_types_ro(self):
        # 'types' should rarely be altered, this check will make
        # doubly sure that a new type isn't accidentally added
        approved_types = OSDB.list_types()

        for osobj in OSDB.list_os():
            if osobj.get_typename() not in approved_types:
                raise AssertionError("OS entry '%s' has OS type '%s'.\n"
                    "The type list should NOT be extended without a lot of "
                    "thought, please make sure you know what you are doing." %
                    (osobj.name, osobj.get_typename()))

    def test_recommended_resources(self):
        conn = utils.URIs.open_testdefault_cached()
        guest = conn.caps.lookup_virtinst_guest()
        assert not OSDB.lookup_os("generic").get_recommended_resources(guest)

        res = OSDB.lookup_os("fedora21").get_recommended_resources(guest)
        assert res["n-cpus"] == 2

        guest.type = "qemu"
        res = OSDB.lookup_os("fedora21").get_recommended_resources(guest)
        assert res["n-cpus"] == 1

    def test_list_os(self):
        full_list = OSDB.list_os()
        pref_list = OSDB.list_os(typename="linux", sortpref=["fedora", "rhel"])
        support_list = OSDB.list_os(only_supported=True)

        assert full_list[0] is not pref_list[0]
        assert len(full_list) > len(support_list)
        assert len(OSDB.list_os(typename="generic")) == 1

        # Verify that sort order actually worked
        found_fedora = False
        found_rhel = False
        for idx, osobj in enumerate(pref_list[:]):
            if osobj.name.startswith("fedora"):
                found_fedora = True
                continue

            for osobj2 in pref_list[idx:]:
                if osobj2.name.startswith("rhel"):
                    found_rhel = True
                    continue
                break
            break

        assert found_fedora and found_rhel
