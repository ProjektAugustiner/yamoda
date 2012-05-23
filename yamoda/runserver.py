"""starts the yamoda server

The runserver.py script starts the yamoda server. It accepts several command line
arguments. For a complete list pass the "--help" option.

"""
from optparse import OptionParser

from yamoda.server import app, db
from yamoda.server.database import User


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--debug', dest='debug', default=True,
                      help='enable Flask debug mode')
    parser.add_option('--init-db', dest='init_db', default=True,
                      help='initializes the database')
    (options, args) = parser.parse_args()
    
    if options.init_db:
        db.drop_all()
        db.create_all()

        print 'adding user:admin pw:password'
        admin = User(name='admin', password='password')
        db.session.add(admin)
        db.session.commit()
    
    #start server
    app.run(debug=options.debug)

