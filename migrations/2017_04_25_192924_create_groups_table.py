from orator.migrations import Migration


class CreateGroupsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('groups') as table:
            table.big_integer('id').unique()
            table.string('title', 50)

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('groups')
