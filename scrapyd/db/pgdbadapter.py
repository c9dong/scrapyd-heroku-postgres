import psycopg2 as pg
import urlparse

class PgDbAdapter:
  def __init__(self, db_url):
    url = urlparse.urlparse(db_url)
    # Remove query strings.
    path = url.path[1:]
    path = path.split('?', 2)[0]

    args = {
      'dbname': path,
      'user': url.username,
      'password': url.password,
      'host': url.hostname,
      'port': url.port,
    }

    conn_string = ' '.join('%s=%s' % item for item in args.items())

    self.conn = pg.connect(conn_string)

  def execute(self, query, args=None):
    try:
      cursor = self.conn.cursor()
      print query
      print args
      cursor.execute(query, args)
    except (pg.InterfaceError, pg.OperationalError) as err:
      raise Exception('bad query: ' + query)

    try:
      results = list(cursor)
    except pg.ProgrammingError:
      results = []

    return results

  def commit(self):
    self.conn.commit()

