#!/usr/bin/env python
"""Script to start the yamoda development server.

The runserver.py script starts the yamoda server. It accepts several command
line arguments. For a complete list pass the "--help" option. Ctrl-C stops the
server.

"""

import yamoda.server.runserver
yamoda.server.runserver.run_server()
