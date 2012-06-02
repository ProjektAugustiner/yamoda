#!/usr/bin/env python
"""Script to start a Python console for a yamoda instance,
e.g. for manual database management.

The local namespace contains the Flask "app" and "db" objects,
as well as all model classes from yamoda.server.database to
play around.
"""

import code
import readline
import rlcompleter

readline.parse_and_bind('tab: complete')

from yamoda.server import app, db
from yamoda.server.database import *

code.interact('yamoda console', local=globals())
