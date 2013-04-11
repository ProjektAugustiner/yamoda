#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
some default settings which can be overriden by command line args or user configuration file.
To override, create a file which looks like this file and set the env var 'YAMODA_SETTINGS' to the path.
'''
import os

DEBUG = True
SECRET_KEY = 'development key'
# where server generated content is cached
GENERATED_DIR = os.path.join(os.getcwd(), "yamoda", "server", "generated")
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
MATPLOTLIB_FONT = {
        'family': 'normal',
        'weight': 'bold',
        'size': 14}
