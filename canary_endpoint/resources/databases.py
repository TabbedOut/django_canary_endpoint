from django.conf import settings
from django.db import connections, DatabaseError

from ..constants import OK, ERROR
from ..decorators import timed
from . import Resource

try:
    # Django 1.7 and later should wrap this exception in a DatabaseError
    from MySQLdb import OperationalError as MySQLError
except ImportError:
    MySQLError = DatabaseError


class Database(Resource):
    """
    Checks the status of a database.

    :param connection: A database connection to query for availability.
    :param statements: The sequence of SQL statements to execute.
    """
    default_statement = 'SELECT 1'

    def __init__(self, name, connection, statements=None, **kwargs):
        self.connection = connection
        self.statements = statements or [self.default_statement]
        super(Database, self).__init__(name, **kwargs)

    @timed(threshold=0.1)
    def check(self):
        result = super(Database, self).check()
        try:
            cursor = self.connection.cursor()
            for sql in self.statements:
                cursor.execute(sql)

            return dict(result, status=OK)
        except (DatabaseError, MySQLError) as e:
            return dict(result, status=ERROR, error=str(e))


class DjangoDatabase(Database):
    """
    Checks a database resource with a Django database connection.
    """
    def __init__(self, name='database', database='default', **kwargs):
        super(DjangoDatabase, self).__init__(
            name=name,
            description=self.get_description(database),
            connection=connections[database],
            **kwargs
        )

    def get_description(self, database):
        template = 'Database "{database}" at {ENGINE}://{HOST}/{NAME}'
        configuration = settings.DATABASES[database].copy()
        configuration.setdefault('HOST', '')
        return template.format(database=database, **configuration)
