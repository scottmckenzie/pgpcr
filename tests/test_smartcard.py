import unittest
from os import environ
from pgpcr.smartcard import *
import subprocess

@unittest.skipUnless("PGPCRSMARTCARD" in environ.keys(), "Smartcard tests"
        " disabled. Set PGPCRSMARTCARD to enable them")
class SmartcardTest(unittest.TestCase):
    def setUp(self):
        subprocess.run(["gpgconf", "--launch", "gpg-agent"])
        self.smart = Smartcard()

    def test_properties(self):
        print()
        print(self.smart.name)
        print(self.smart.sex)
        print(self.smart.login)
        print(self.smart.reader)
        print(self.smart.vendor)
        print(self.smart.serial)

    def test_set_properties(self):
        print()
        self.smart.name = "First Last"
        print(self.smart.name)
        self.smart.url = "https://example.com"
        print(self.smart.url)
        self.smart.sex = "m"
        print(self.smart.sex)
        self.smart.login = "login"
        print(self.smart.login)

    def test_set_PIN(self):
        self.smart.setPIN()
