from orator.migrations import Migration


class CreateListXItemTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('list_x_item') as table:
            table.increments('id')
            table.integer('list_id').unsigned()
            table.integer('item_id').unsigned()
            table.big_integer('user_id')
            table.float('price')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('list_x_item')
