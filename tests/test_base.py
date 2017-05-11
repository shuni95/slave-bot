from unittest import TestCase
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator import DatabaseManager, Model

class OratorTestCase(TestCase):

    db = None

    def setUp(self):
        self.db = DatabaseManager({
            'default': 'sqlite',
            'sqlite': {
                'driver': 'sqlite',
                'database': ':memory:'
            }
        })

        repository = DatabaseMigrationRepository(self.db, 'migrations')
        migrator = Migrator(repository, self.db)  # db is the DatabaseManager instance

        if not migrator.repository_exists():
            repository.create_repository()

        migrator.set_connection('sqlite')  # Needed only if it's not the default database
        migrator.run('../migrations')  ## migrations_path is the directory where you migration files are

        Model.set_connection_resolver(self.db)
