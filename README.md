yamoda
======

Run Dependencies
----------------

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
* psycopg2 (for PostgresQL backend, can be disabled)
* meta

Test Dependencies
-----------------

* nose

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
    wget https://github.com/ProjektAugustiner/yamoda/raw/<branch>/database.cfg

(optional) Customize database eggs: Edit database.cfg and comment out unwanted database eggs

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

from zc.buildout toplevel dir.

Create test data in selected DB (default is SQLite):

    bin/init_db --database sqlite | postgres | mysql


Running The Development Server
------------------------------

from zc.buildout toplevel dir.

Start it with:

     bin/run_server [--debug True]
    
To select the DB backend (default is SQLite):

    bin/run_server --database sqlite | postgres | mysql

To set server listening socket:

    bin/run_server --host 0.0.0.0 --port 5555


Starting IPython Environment For Testing
----------------------------------------

from zc.buildout toplevel dir.

Start with:

    bin/ipython

and select a database engine.


Running With GUnicorn
---------------------

from zc.buildout toplevel dir.

gUnicorn can be installed in the virtualenv:

    bin/pip install gunicorn

Use the intepreter 'py' created by zc.buildout to run the gunicorn start script, for example:

    bin/py bin/gunicorn -b "127.0.0.1:5000" 'yamoda.server:make_app(ADDITIONAL_FLASK_SETTING="bla", SETTING=True)' 


Running all nose tests
----------------------

Run:

    bin/nosetests


Testing importers
-----------------

TODO

    
