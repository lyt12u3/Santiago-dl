import sqlite3

class Subjects:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS subjects (id int auto_increment primary key, nure_group text, subjects text)')

    def subjects_exist(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM subjects WHERE nure_group = ?', (nure_group,)).fetchall()
            return bool(len(result))

    def set_subjects(self, nure_group, subjects):
        with self.connection:
            subjects_line = ','.join(subjects)
            if self.subjects_exist(nure_group):
                return self.cursor.execute('UPDATE subjects SET subjects = ? WHERE nure_group = ?', (subjects_line, nure_group))
            else:
                return self.cursor.execute('INSERT INTO subjects (nure_group, subjects) VALUES (?,?)', (nure_group, subjects_line))

    def get_subjects(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT subjects FROM subjects WHERE nure_group = ?', (nure_group,)).fetchall()
            return result[0][0]
