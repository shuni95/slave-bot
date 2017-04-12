import pymysql.cursors

class Connection():
    @staticmethod
    def open():
        return pymysql.connect(host='localhost', user='root', password='root',
                               db='slave', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)