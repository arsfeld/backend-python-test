"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migrate
"""
from docopt import docopt
import subprocess
import os
import sys
import sqlite3

from alayatodo import app


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError, ex:
        print ex.output
        sys.exit(1)

def migrate():
    conn = sqlite3.connect(app.config['DATABASE'])
    with conn:
        conn.execute('CREATE TABLE IF NOT EXISTS migrations (name VARCHAR(255) UNIQUE);')
        for (dirpath, dirnames, filenames) in os.walk('./resources/migrations'):
            for filename in sorted(filenames):
                if conn.execute('SELECT COUNT(*) FROM migrations WHERE name=?', (filename,)).fetchone()[0] > 0:
                    continue
                print "Running %s" % (filename,)
                with open(os.path.join(dirpath, filename)) as f:
                    conn.executescript(f.read())
                print conn.execute('INSERT INTO migrations(name) VALUES (?)', (filename,)).fetchall()


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        print "AlayaTodo: Database initialized."
    elif args['migrate']:
        print "AlayaTodo: Starting migration..."
        migrate()
        print "AlayaTodo: All files migrated!"
    else:
        app.run(use_reloader=True)
