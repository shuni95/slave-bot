from orator.seeds import Seeder

class DatabaseSeeder(Seeder):

    def run(self):
        """
        Run the database seeds.
        """
        self.call(ItemTableSeeder)

class ItemTableSeeder(Seeder):

    def run(self):
        """
        Run the database seeds.
        """
        self.db.table('items').insert({'name': 'Empanada', 'price': 350,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Sporade', 'price': 250,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Enrollado', 'price': 350,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Free Tea', 'price': 200,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Agua Cielo', 'price': 150,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Kilometrico', 'price': 800,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Batimix', 'price': 350,
                                       'is_default': True})
        self.db.table('items').insert({'name': 'Cacho', 'price': 90,
                                       'is_default': True})
