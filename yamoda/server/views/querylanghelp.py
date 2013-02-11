#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 27.08.2012
@author: dpausp (Tobias Stenzel)

Return content for query language help tabs via AJAX.
'''

import logging as logg

from flask.ext.login import login_required

from yamoda.server import app

QUERYLANG_HELP_CONTENTS = {
"find": """\
<h3>Result Type</h3>
<p>A search can return sets or datas. The behaviour can be selected with <em>find</em>:</p>
<p>Depending on the selected return type, different query options are available.</p>
<p>Default: If nothing was specified, sets will be returned.</p>
<ul>
<li>To query for sets: <code>find: sets</code>
<li>To query for datas: <code>find: datas</code>
</ul>
""",

"param-filter": """\
<h3>Parameter Filter ('datas' only)</h3>
<p>Checks if the value of a parameter satisfies a condition.</p>
<p>Conditions can be joined with <em>or</em>.
This means that at least one of the conditions must be satisfied to include a data in the result list.</p>
<p>The Parameter in the example is called <em>T</em>.</p>
<ul>
<li>Value less than 100: <code>T: &lt; 100</code>
<li>Value greater than 100: <code>T: &gt; 100</code>
<li>Value between 100 and 200: <code>T: 100 to 200</code>
<li>Alternative condition I: <code>T: 100 to 200 or 300 to 400</code> 
<li>Alternative condition II: <code>T: 10 to 50 or &gt; 1.2e6</code>
</ul>
""",

"sort": """\
<h3>Sort By Value ('datas' only)</h3>
<p>Data query results can be sorted by parameter values.</p>
<ul>
<li>To sort by parameter value for T (ascending, lowest first) : <code>sort: T</code>
<li>To sort by parameter value for omega (descending, highest first) : <code>sort: omega.desc</code>
<li>To sort by T, then by omega: <code>sort: T omega</code>
</ul>
""",

"other": """\
<h3>Other Query Options</h3>
<ul>
<li>Only show specified parameters in result: <code>visible: T omega</code>
<li>Limit number of results to 50: <code>limit: 50</code>
<li>(datas only) Datas must belong to Context "vsm": <code>context: vsm</code>
<li>(sets only) Set was created by "tim": <code>user: tim</code>
<li>(sets only) Set was created in this date range: <code>created: 11 January 2012 to 23 March 2013</code>
</ul>
""",

"example-datas": """\
<h3>Complete Example For Datas Query</h3>
<pre>
find: datas
T: 10 to 300 or > 500
omega: < 1e6
sort: omega.desc
limit: 20
show: T omega
</pre>
""",

"example-sets": """\
<h3>Complete Example For Sets Query</h3>
<pre>
find: sets
user: admin
created: 11 January 2012 to 23 March 2013
limit: 10
</pre>
"""
}


@app.route('/gethelptext/<string:name>')
@login_required
def get_helptext(name):
    return QUERYLANG_HELP_CONTENTS[name]
