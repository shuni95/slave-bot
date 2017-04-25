from orator.migrations import Migration


class CreateListsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('lists') as table:
            table.increments('id')
            table.char('status', 1)
            table.integer('group_id').unsigned()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('lists')
