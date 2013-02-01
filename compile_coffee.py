#!/usr/bin/env python
import os
import glob
import logging as logg
from subprocess import call

logg.basicConfig(level=logg.DEBUG)
os.chdir("yamoda/server/static/gen_js/")
coffee_files = glob.glob("*.coffee")
logg.info("compiling %s files", len(coffee_files))

for cf in coffee_files:
    logg.info("compiling %s", cf)
    call(["coffee", "-c", cf])
