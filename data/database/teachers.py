import sqlite3

class Teachers:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS teachers (id int auto_increment primary key, name text, code int)')

    def teacher_exist(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM teachers WHERE name = ?', (name,)).fetchall()
            return bool(len(result))

    def add_teacher(self, name, code):
        with self.connection:
            if not self.teacher_exist(name):
                return self.cursor.execute('INSERT INTO teachers (name, code) VALUES (?,?)', (name, code))

    def delete_teacher(self, name):
        with self.connection:
            if self.teacher_exist(name) == 1:
                return self.cursor.execute('DELETE FROM teachers WHERE name = ?', (name,))

    def get_teachers(self):
        with self.connection:
            result = self.cursor.execute('SELECT name, code FROM teachers').fetchall()
            return result

    def get_teachers_names(self):
        with self.connection:
            answer = self.cursor.execute('SELECT name FROM teachers').fetchall()
            result = []
            for el in answer:
                result.append(el[0])
            return result

    def get_code(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT code FROM teachers WHERE name = ?', (name,)).fetchall()
            return result[0][0]

class AllTeachers:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS all_teachers (id int auto_increment primary key, name text, code int)')

    def teacher_exist(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM all_teachers WHERE name = ?', (name,)).fetchall()
            return bool(len(result))

    def add_teacher(self, name, code):
        with self.connection:
            if not self.teacher_exist(name):
                return self.cursor.execute('INSERT INTO all_teachers (name, code) VALUES (?,?)', (name,code))

    def get_code(self, name):
        with self.connection:
            result = self.cursor.execute('SELECT code FROM all_teachers WHERE name = ?', (name,)).fetchall()
            return result[0][0]

    def get_name(self, code):
        with self.connection:
            result = self.cursor.execute('SELECT name FROM all_teachers WHERE code = ?', (code,)).fetchall()
            return result[0][0]

    def get_teachers(self):
        with self.connection:
            result = self.cursor.execute('SELECT name, code FROM all_teachers').fetchall()
            return result

    def get_teachers_names(self):
        with self.connection:
            answer = self.cursor.execute('SELECT name FROM all_teachers').fetchall()
            result = []
            for teacher in answer:
                result.append(teacher[0])
            return result

    def truncate(self):
        with self.connection:
            result = self.cursor.execute('DELETE FROM all_teachers')
