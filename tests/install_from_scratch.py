# coding: utf-8

import os
import tempfile
import pexpect
import unittest

from modoboa.lib.sysutils import exec_cmd


class DeployTest(unittest.TestCase):
    dbtype = "mysql"
    dbhost = "localhost"
    projname = "modoboa_test"
    dbuser = "travis"
    dbpassword = ""

    def setUp(self):
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        path = os.path.join(self.workdir, self.projname)
        core_apps = ["modoboa.core", "modoboa.lib"]
        cmd = "python manage.py test {0}".format(
            " ".join(core_apps),
        )
        code, output = exec_cmd(cmd, capture_output=False, cwd=path)
        self.assertEqual(code, 0)

    def test_standard(self):
        timeout = 2
        cmd = (
            "modoboa-admin.py deploy --collectstatic {0}"
            .format(self.projname)
        )
        child = pexpect.spawn(cmd, cwd=self.workdir)
        fout = open('install_from_scratch.log', 'w')
        child.logfile = fout
        child.expect("Database type \(mysql, postgres or sqlite3\):", timeout=timeout)
        child.sendline(self.dbtype)
        child.expect("Database host \(default: 'localhost'\):", timeout=timeout)
        child.sendline(self.dbhost)
        child.expect("Database port \(default: '3306'\):", timeout=timeout)
        child.sendline('3306')
        child.expect("Database name:", timeout=timeout)
        child.sendline(self.projname)
        child.expect("Username:", timeout=timeout)
        child.sendline(self.dbuser)
        child.expect("Password:", timeout=timeout)
        child.sendline(self.dbpassword)
        child.expect("Under which domain do you want to deploy modoboa?", timeout=timeout)
        child.sendline("localhost")
        child.wait()
        fout.close()
        self.assertEqual(child.exitstatus, 0)

    def test_silent(self):
        dburl = "default:%s://%s:%s@%s/%s" \
            % (self.dbtype, self.dbuser, self.dbpassword,
               self.dbhost, self.projname)
        cmd = (
            "modoboa-admin.py deploy --collectstatic "
            "--dburl %s --domain %s %s"
            % (dburl, 'localhost', self.projname)
        )
        code, output = exec_cmd(cmd, cwd=self.workdir)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
