import sqlite3

class Links:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS links (id int auto_increment primary key, user_id int, nure_group text, subject text, subject_type text, link text)')

    def link_exist(self, user_id, nure_group, subject, subject_type):
        with self.connection:
            if self.is_null(user_id, nure_group, subject):
                link = self.cursor.execute('SELECT link FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type IS NULL',(user_id, nure_group, subject)).fetchall()
                self.cursor.execute('DELETE FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type IS NULL',(user_id, nure_group, subject))
                self.cursor.execute('INSERT INTO links (user_id, nure_group, subject, subject_type, link) VALUES (?,?,?,?,?)',(user_id, nure_group, subject, 'Лк', link[0][0]))
                self.cursor.execute('INSERT INTO links (user_id, nure_group, subject, subject_type, link) VALUES (?,?,?,?,?)',(user_id, nure_group, subject, 'Пз', link[0][0]))
                self.cursor.execute('INSERT INTO links (user_id, nure_group, subject, subject_type, link) VALUES (?,?,?,?,?)',(user_id, nure_group, subject, 'Лб', link[0][0]))
            result = self.cursor.execute('SELECT * FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type = ?', (user_id, nure_group, subject, subject_type)).fetchall()
            return bool(len(result))

    def any_link_exist(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM links WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject)).fetchall()
            return bool(len(result))

    def is_null(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type IS NULL', (user_id, nure_group, subject)).fetchall()
            return bool(len(result))

    def add_link(self, user_id, nure_group, subject, subject_type, link):
        with self.connection:
            return self.cursor.execute('INSERT INTO links (user_id, nure_group, subject, subject_type, link) VALUES (?,?,?,?,?)', (user_id, nure_group, subject, subject_type, link))

    def update_link(self, user_id, nure_group, subject, subject_type, link):
        with self.connection:
            return self.cursor.execute('UPDATE links SET link = ? WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type = ?', (link, user_id, nure_group, subject, subject_type))

    def get_link(self, user_id, nure_group, subject, subject_type):
        with self.connection:
            result = self.cursor.execute('SELECT link FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type = ?', (user_id, nure_group, subject, subject_type)).fetchall()
            return result[0][0]

    def delete_link(self, user_id, nure_group, subject, subject_type):
        with self.connection:
            return self.cursor.execute('DELETE FROM links WHERE user_id = ? AND nure_group = ? AND subject = ? AND subject_type = ?', (user_id, nure_group, subject, subject_type))

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE FROM links WHERE user_id = ?', (user_id,))
