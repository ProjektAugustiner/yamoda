#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 22.04.2013
@author: dpausp (Tobias Stenzel)

Test serialization and deserialization
'''
from __future__ import division, absolute_import
from pprint import pformat

import yamoda.query.test.testqueries as tq
from yamoda.query.serialization import to_json, from_json
from yamoda.query.test.helpers import compare_dict_items


def test_serialize():
    expected = tq.testquery_datas2.dict
    js = to_json(expected)
    decoded = from_json(js)
    assert decoded == expected, ("deserialization result was\n{}, expected:\n\n{}. Diff is:\n{}".
                                            format(pformat(decoded),
                                                   pformat(expected),
                                                   compare_dict_items(decoded, expected)))
