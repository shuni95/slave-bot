from orator.migrations import Migration


class CreatePaymentsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('payments') as table:
            table.increments('id')
            table.integer('list_id').unsigned()
            table.big_integer('user_id')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('payments')
