#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 08.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import logging
from yamoda.server.database.datamodel import Entry

logg = logging.getLogger("yamoda.view_helpers")


def get_entries(datas, params):
    """Get entries for params.
    Moved from views/set.py.
    FIXME: this is quick and dirty, and way too inefficient.  Must be
    rewritten using fewer queries.
    """
    entries = []
    for d in datas:
        entries.append([])
        for p in params:
            entry = Entry.query.filter_by(data=d, parameter=p).first()
            entries[-1].append(entry)

    return entries
