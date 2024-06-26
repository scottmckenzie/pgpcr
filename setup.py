#!/usr/bin/python3

from setuptools import setup
from setuptools.command.build_py import build_py
from tests import helpers

class BuildCommand(build_py):
    def run(self):
        self.run_command("compile_catalog")
        build_py.run(self)

setup(name="PGP Clean Room",
      version="0.1",
      description="",
      author="Jacob Adams",
      author_email="tookmund@gmail.com",
      url="https://salsa.debian.org/tookmund-guest/pgpcr",
      packages=["pgpcr"],
      install_requires=["gpg", "snack"],
      setup_requires=["babel"],
      cmdclass={'build_py': BuildCommand},
     )
