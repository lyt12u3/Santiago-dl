import sqlite3

class Notify:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS notify (id int auto_increment primary key, user_id int, nure_group, subject text, status bool)')

    def notify_exist(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM notify WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject)).fetchall()
            return bool(len(result))

    def add_notify(self, user_id, nure_group, subject, status = True):
        with self.connection:
            return self.cursor.execute('INSERT INTO notify (user_id, nure_group, subject, status) VALUES (?,?,?,?)', (user_id, nure_group, subject, status))

    def update_notify(self, user_id, nure_group, subject, status):
        with self.connection:
            return self.cursor.execute('UPDATE notify SET status = ? WHERE user_id = ? AND nure_group = ? AND subject = ?', (status, user_id, nure_group, subject))

    def update_all_notity(self, user_id, nure_group, status):
        with self.connection:
            return self.cursor.execute('UPDATE notify SET status = ? WHERE user_id = ? AND nure_group = ?', (status, user_id, nure_group))

    def get_notify(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT status FROM notify WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject)).fetchall()
            return result[0][0]

    def get_all_notify(self, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT user_id, nure_group FROM notify WHERE nure_group = ? AND subject = ? AND status = 1', (nure_group, subject)).fetchall()
            return result

    def has_positive_notify(self, user_id, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM notify WHERE user_id = ? AND nure_group = ? AND status = 1',(user_id, nure_group)).fetchall()
            return bool(len(result))

    def delete_notify(self, user_id, nure_group, subject):
        with self.connection:
            return self.cursor.execute('DELETE FROM notify WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject))

    def delete_all_notify(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE FROM notify WHERE user_id = ?', (user_id,))
