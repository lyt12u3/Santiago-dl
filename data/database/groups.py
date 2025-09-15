import sqlite3

class Groups:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS nure_groups (id int auto_increment primary key, nure_group text, link_code int)')

    def group_exist(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM nure_groups WHERE nure_group = ?', (nure_group,)).fetchall()
            return bool(len(result))

    def add_group(self, nure_group, link_code):
        with self.connection:
            if not self.group_exist(nure_group):
                return self.cursor.execute('INSERT INTO nure_groups (nure_group, link_code) VALUES (?,?)', (nure_group,link_code))

    def delete_group(self, nure_group):
        with self.connection:
            if self.group_exist(nure_group) == 1:
                return self.cursor.execute('DELETE FROM nure_groups WHERE nure_group = ?', (nure_group,))

    def get_groups(self):
        with self.connection:
            result = self.cursor.execute('SELECT nure_group, link_code FROM nure_groups').fetchall()
            return result

    def get_groups_names(self):
        with self.connection:
            answer = self.cursor.execute('SELECT nure_group FROM nure_groups').fetchall()
            result = []
            for el in answer:
                result.append(el[0])
            return result

    def get_code(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT link_code FROM nure_groups WHERE nure_group = ?', (nure_group,)).fetchall()
            return result[0][0]

class AllGroups:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS all_nure_groups (id int auto_increment primary key, nure_group text, link_code int)')

    def group_exist(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM all_nure_groups WHERE nure_group = ?', (nure_group,)).fetchall()
            return bool(len(result))

    def add_group(self, nure_group, link_code):
        with self.connection:
            if not self.group_exist(nure_group):
                return self.cursor.execute('INSERT INTO all_nure_groups (nure_group, link_code) VALUES (?,?)', (nure_group,link_code))

    def get_code(self, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT link_code FROM all_nure_groups WHERE nure_group = ?', (nure_group,)).fetchall()
            return result[0][0]

    def get_groups(self):
        with self.connection:
            result = self.cursor.execute('SELECT nure_group, link_code FROM all_nure_groups').fetchall()
            return result

    def get_groups_names(self):
        with self.connection:
            answer = self.cursor.execute('SELECT nure_group FROM all_nure_groups').fetchall()
            result = []
            for group in answer:
                result.append(group[0])
            return result

    def truncate(self):
        with self.connection:
            result = self.cursor.execute('DELETE FROM all_nure_groups')
