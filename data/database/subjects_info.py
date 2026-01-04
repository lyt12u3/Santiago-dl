import sqlite3

class SubjectsInfo:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS subjects_info (id int auto_increment primary key, nure_group text, subject text, type text, full_name test, teacher text)')

    def exist(self, nure_group, subject, type):
        with self.connection:
            result = self.cursor.execute('SELECT 1 FROM subjects_info WHERE nure_group = ? AND subject = ? AND type = ?',(nure_group,subject,type)).fetchall()
            return bool(len(result))

    def set_subject_info(self, nure_group, subject, type, full_name, teacher):
        with self.connection:
            if self.exist(nure_group, subject, type):
                return self.cursor.execute('UPDATE subjects_info SET full_name = ?, teacher = ? WHERE nure_group = ? AND subject = ? AND type = ?', (full_name, teacher, nure_group, subject, type))
            else:
                return self.cursor.execute('INSERT INTO subjects_info (nure_group, subject, type, full_name, teacher) VALUES (?,?,?,?,?)', (nure_group, subject, type, full_name, teacher))

    def get_teacher(self, nure_group, subject, type):
        with self.connection:
            if self.exist(nure_group, subject, type):
                result = self.cursor.execute('SELECT teacher FROM subjects_info WHERE nure_group = ? AND subject = ? AND type = ?',(nure_group, subject, type)).fetchall()
                return result[0][0]
            return None

    def get_full_name(self, nure_group, subject, type):
        with self.connection:
            if self.exist(nure_group, subject, type):
                result = self.cursor.execute('SELECT full_name FROM subjects_info WHERE nure_group = ? AND subject = ? AND type = ?',(nure_group, subject, type)).fetchall()
                return result[0][0]
            return None