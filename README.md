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


Installing via zc.buildout + virtualenv
---------------------------------------

Recommended install method.
First, install Python 2.7 and virtualenv on your machine. Everything else will be fetched by zc.buildout.
We use zc.buildout 2.0.

Create virtualenv:

    virtualenv --distribute --no-site-packages yamoda_buildout     
    cd yamoda_buildout
    
Get bootstrap.py and buildout.cfg from yamoda <branch>:

    wget http://downloads.buildout.org/2/bootstrap.py
    wget https://github.com/ProjektAugustiner/yamoda/raw/<branch>/buildout.cfg


Install numpy:

    bin/pip install numpy
    
Bootstrap and buildout:

    bin/python bootstrap.py
    bin/buildout -c buildout.cfg
    

Some coffeescript modules in yamoda/server/static/js must be compiled before the app can be used. Run:

    cd src/yamoda
    ../../bin/python compile_coffee.py


Executable scripts are installed in bin/, see below for help


Creating Test Data
------------------

Create test data in selected DB (default is SQLite):

    python init_db.py --database sqlite | postgres | mysql

Running The Server
------------------

Start it with:

    python run_server.py [--debug True]
    
To select the DB backend (default is SQLite):

    python run_server.py --database sqlite | postgres | mysql


Testing importers
-----------------
