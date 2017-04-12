from connection import Connection

class Group(object):
    @staticmethod
    def find(chat_id):
        db = Connection.open()
        group = None
        try:
            with db.cursor() as cursor:
                sql = "SELECT * FROM groups WHERE telegram_chat_id = %s LIMIT 1;"
                cursor.execute(sql, (chat_id))
                group = cursor.fetchone()
        finally:
            db.close()
        return group

    @staticmethod
    def create(data):
        db = Connection.open()
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO groups (title, telegram_chat_id) VALUES (%s, %s);"
                cursor.execute(sql, (data.title, data.id))
            db.commit()
        finally:
            db.close()