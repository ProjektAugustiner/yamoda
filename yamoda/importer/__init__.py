#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Importer submodules.
"""

import sys

# For every importer submodule, there must be an entry in this dictionary
# mapping the submodule name to a description

importers = {
    'mira_single': ('MIRA single counter data',),
}

def list_importers():
    return importers.iteritems()

def load_importer(name):
    """Load the given importer module and return its Importer class."""
    if name not in importers:
        raise ValueError('importer %r not found' % name)
    modname = 'yamoda.importer.%s' % name
    __import__(modname)
    return sys.modules[modname].Importer
