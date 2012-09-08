#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 08.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
from yamoda.server.database.datamodel import Entry


def get_pvalues(datas, params):
    """Get values for params.
    Moved from views/set.py.
    FIXME: this is quick and dirty, and way too inefficient.  Must be
    rewritten using fewer queries.
    """
    pvalues = []
    for d in datas:
        pvalues.append([])
        for p in params:
            pvalue = Entry.query.filter_by(data=d, parameter=p).first()
            pvalues[-1].append(pvalue.value if pvalue else None)

    return pvalues
