from connection import Connection

class User(object):
    @staticmethod
    def find(chat_id):
        db = Connection.open()
        user = None
        try:
            with db.cursor() as cursor:
                sql = "SELECT * FROM users WHERE telegram_chat_id = %s LIMIT 1;"
                cursor.execute(sql, (chat_id))
                user = cursor.fetchone()
        finally:
            db.close()
        return user

    @staticmethod
    def create(data):
        db = Connection.open()
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO users (name, username, telegram_chat_id) VALUES (%s, %s, %s);"
                cursor.execute(sql, (data.first_name, data.username, data.id))
            db.commit()
        finally:
            db.close()
