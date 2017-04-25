from orator import DatabaseManager, Model
from orator.orm import has_many, belongs_to, belongs_to_many

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
    __fillable__ = ['status']

    @belongs_to
    def group(self):
        return Group

    @belongs_to_many('list_x_item')
    def items(self):
        return Item

class Item(Model):
    __fillable__ = ['name', 'price']

    @belongs_to_many('list_x_item')
    def lists(self):
        return List
