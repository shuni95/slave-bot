from orator import DatabaseManager, Model
from orator.orm import has_many, belongs_to, belongs_to_many, accessor, scope

config = {
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'slave',
        'user': 'root',
        'password': 'root',
        'prefix': '',
        'charset': 'utf8mb4'
    }
}

db = DatabaseManager(config)
Model.set_connection_resolver(db)

class User(Model):
    __fillable__ = ['name', 'username', 'telegram_chat_id']
    __timestamps__ = False

class Group(Model):
    __fillable__ = ['title', 'telegram_chat_id']
    __timestamps__ = False

    @has_many
    def lists(self):
        return List

class List(Model):
    OPENED = 'O'
    CLOSED = 'C'
    DONE = 'D'

    __fillable__ = ['status']

    @belongs_to
    def group(self):
        return Group

    @belongs_to_many('list_x_item')
    def items(self):
        return Item

    @scope
    def opened(self, query):
        return query.where_status(List.OPENED)

    @scope
    def closed(self, query):
        return query.where_status(List.CLOSED)

    def open(self):
        self.status = List.OPENED
        self.save()

    def close(self):
        self.status = List.CLOSED
        self.save()

class Item(Model):
    __fillable__ = ['name', 'price']

    @belongs_to_many('list_x_item')
    def lists(self):
        return List

    @accessor
    def price_format(self):
        price = float(self.get_raw_attribute('price'))
        return 'S/ {0:.2g}'.format(price / 100)

    @scope
    def defaults(self, query):
        return query.where_is_default(True)
