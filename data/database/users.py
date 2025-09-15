import sqlite3

class Users:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
            return bool(len(result))
    def add_user(self, user_id, nure_group, notify_status = False):
        with self.connection:
            return self.cursor.execute('INSERT INTO users (user_id, nure_group, notify_status) VALUES (?,?,?)', (user_id, nure_group, notify_status))
    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    def update_notify_status(self, user_id, notify_status):
        with self.connection:
            return self.cursor.execute('UPDATE users SET notify_status = ? WHERE user_id = ?', (notify_status, user_id))
    def update_nure_group(self, user_id, nure_group):
        with self.connection:
            return self.cursor.execute('UPDATE users SET nure_group = ? WHERE user_id = ?', (nure_group, user_id))
    def get_notify_status(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT notify_status FROM users WHERE user_id = ?', (user_id,)).fetchall()
            # return bool(result)
            return result[0][0]
    def get_group(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT nure_group FROM users WHERE user_id = ?', (user_id,)).fetchall()
            return result[0][0]
    def get_notify_users(self):
        with self.connection:
            result = self.cursor.execute('SELECT user_id, nure_group FROM users WHERE notify_status = 1').fetchall()
            return result
    def get_users_in_group(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT user_id FROM users WHERE nure_group = ?', (nure_group,)).fetchall()
            return result
    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, user_id int, nure_group varchar(25), notify_status bool)')
            # self.connection.commit()
    def read_all(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM users').fetchall()
            return result
    def clear(self):
        with self.connection:
            return self.cursor.execute('DELETE FROM users')
    def close(self):
        self.connection.close()
