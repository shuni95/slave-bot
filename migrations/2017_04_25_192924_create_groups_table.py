from orator.migrations import Migration


class CreateGroupsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('groups') as table:
            table.increments('id')
            table.string('title', 50)
            table.big_integer('telegram_chat_id')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('groups')
