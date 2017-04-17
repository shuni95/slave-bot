from eloquent import DatabaseManager, Model

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
    __timestamps__ = False