from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.big_integer('id').unique()
            table.string('name', 50)
            table.string('username', 50)

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
