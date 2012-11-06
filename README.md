yamoda
======

Dependencies
------------

* Python 2.7
* SQLAlchemy
* Flask
* Flask-Login
* Flask-SQLAlchemy
* py-bcrypt
* python-markdown2
* numpy
* quantities (version >= 0.10.0)
* Parcon
* DateRangeParser
* mimerender
* Coffeescript compiler (on node.js)
* nose (only for unit tests)
* psycopg2 (for PostgresQL backend)

Licensing
---------

You should have received a copy of the [GNU General Public License][] along 
with yamoda; see the file COPYING.
  [GNU General Public License]: http://www.gnu.org/licenses/gpl.html

Creating Test Data
------------------

Create test data in selected DB (default is SQLite):

    python init_db.py --database sqlite | postgres | mysql

Running The Server
------------------

Start it with:

    python runserver.py [--debug True]
    
To select the DB backend (default is SQLite):

    python runserver.py --database sqlite | postgres | mysql

