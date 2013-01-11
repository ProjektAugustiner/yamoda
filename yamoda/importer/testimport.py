"""testing the importer.
"""

import optparse
import sys

from yamoda.server import db
from yamoda.server.database import User, Group, Context, Set

from yamoda.importer import load_importer
from yamoda.importer.base import MissingInfo


def test_import(argv=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-a', action='store_true', dest='autoparams', default=False,
                      help='automatically add missing parameters')
    parser.add_option('-s', type='int', dest='setid',
                      help='data set to import to, default is to create new')
    opts, args = parser.parse_args(argv[1:])

    impname = args[0]
    filenames = args[1:]

    ctx = Context.query.get(1)
    usr = User.query.filter_by(name='admin').first()
    grp = Group.query.filter_by(name='admin').first()
    baseset = Set(name='imported', user=usr, group=grp)

    importer = load_importer(impname)(ctx, baseset)
    userinfo = {}
    try:
        while 1:
            try:
                importer.import_items(filenames, userinfo)
            except MissingInfo, err:
                if opts.autoparams:
                    for pname, pwhat, _ in err.info:
                        if pwhat == 'new_param':
                            userinfo[pname] = {}
                        else:
                            raise RuntimeError('do not know how to supply user info '
                                               'of type %s' % pwhat)
                    continue
                else:
                    print 'Parameters are missing:'
                    for p in err.info:
                        print p[0], p[1]
                        if p[2]: print p[2]
            break
        db.session.add(baseset)
        db.session.commit()
    except:
        db.session.rollback()
        raise
