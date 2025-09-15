import sqlite3

class Marks:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS marks (id int auto_increment primary key, nure_group text, subject text, subject_type text, link text)')

    def marklink_exist(self, nure_group, subject, subject_type):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM marks WHERE nure_group = ? AND subject = ? AND subject_type = ?', (nure_group, subject, subject_type)).fetchall()
            return bool(len(result))

    def any_marklink_exist(self, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM marks WHERE nure_group = ? AND subject = ?', (nure_group, subject)).fetchall()
            return bool(len(result))

    def add_marklink(self, nure_group, subject, subject_type, link):
        with self.connection:
            return self.cursor.execute('INSERT INTO marks (nure_group, subject, subject_type, link) VALUES (?,?,?,?)', (nure_group, subject, subject_type, link))

    def update_marklink(self, nure_group, subject, subject_type, link):
        with self.connection:
            return self.cursor.execute('UPDATE marks SET link = ? WHERE nure_group = ? AND subject = ? AND subject_type = ?', (link, nure_group, subject, subject_type))

    def get_marklink(self, nure_group, subject, subject_type):
        with self.connection:
            result = self.cursor.execute('SELECT link FROM marks WHERE nure_group = ? AND subject = ? AND subject_type = ?', (nure_group, subject, subject_type)).fetchall()
            return result[0][0]

    def delete_marklink(self, nure_group, subject, subject_type):
        with self.connection:
            return self.cursor.execute('DELETE FROM marks WHERE nure_group = ? AND subject = ? AND subject_type = ?', (nure_group, subject, subject_type))
