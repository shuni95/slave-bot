from orator.migrations import Migration


class CreateItemsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('items') as table:
            table.increments('id')
            table.string('name')
            table.float('price')
            table.big_integer('group_id')
            table.soft_deletes()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('items')
