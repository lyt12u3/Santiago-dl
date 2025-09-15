import sqlite3

class Display:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS display (id int auto_increment primary key, user_id int, nure_group text, display_subjects text)')

    def display_exist(self, user_id, nure_group):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM display WHERE user_id = ? AND nure_group = ?', (user_id, nure_group)).fetchall()
            return bool(len(result))

    def add_display(self, user_id, nure_group, subject):
        with self.connection:
            if self.display_exist(user_id, nure_group):
                current_display = self.get_display(user_id, nure_group)
                current_display_list = current_display.split(",")
                current_display_list.append(subject)
                new_display = ",".join(current_display_list)
                return self.cursor.execute('UPDATE display SET display_subjects = ? WHERE user_id = ? AND nure_group = ?',(new_display, user_id, nure_group))
            else:
                return self.cursor.execute('INSERT INTO display (user_id, nure_group, display_subjects) VALUES (?,?,?)',(user_id, nure_group, subject))

    def remove_display(self, user_id, nure_group, subject):
        with self.connection:
            current_display = self.get_display(user_id, nure_group)
            current_display_list = current_display.split(",")
            current_display_list.remove(subject)
            display_subjects = ",".join(current_display_list)
            return self.cursor.execute('UPDATE display SET display_subjects = ? WHERE user_id = ? AND nure_group = ?',(display_subjects, user_id, nure_group))

    def has_display(self, user_id, nure_group, subject):
        with self.connection:
            if self.display_exist(user_id, nure_group):
                current_display = self.get_display(user_id, nure_group)
                display_status = subject in current_display
                return display_status
            else:
                return False

    def set_display(self, user_id, nure_group, subjects_line):
        with self.connection:
            if self.display_exist(user_id, nure_group):
                return self.cursor.execute('UPDATE display SET display_subjects = ? WHERE user_id = ? AND nure_group = ?',(subjects_line, user_id, nure_group))
            else:
                return self.cursor.execute('INSERT INTO display (user_id, nure_group, display_subjects) VALUES (?,?,?)',(user_id, nure_group, subjects_line))

    def update_display(self, user_id, nure_group, subject):
        with self.connection:
            current_display = self.get_display(user_id, nure_group)
            current_display_list = current_display.split(",")
            if subject in current_display_list:
                current_display_list.remove(subject)
            else:
                current_display_list.append(subject)
            new_display = ",".join(current_display_list)
            return self.cursor.execute('UPDATE display SET display_subjects = ? WHERE user_id = ? AND nure_group = ?',(new_display, user_id, nure_group))

    def get_display(self, user_id, nure_group):
        with self.connection:
            if self.display_exist(user_id, nure_group):
                result = self.cursor.execute('SELECT display_subjects FROM display WHERE user_id = ? AND nure_group = ?', (user_id, nure_group)).fetchall()
                return result[0][0]

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE FROM display WHERE user_id = ?', (user_id,))


class DisplayNew:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def check_file(self):
        with self.connection:
            return self.cursor.execute('CREATE TABLE IF NOT EXISTS display_new (id int auto_increment primary key, user_id int, nure_group, subject text, status bool)')

    def display_exist(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM display_new WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject)).fetchall()
            return bool(len(result))

    def user_exist(self, user_id, nure_group):
            result = self.cursor.execute('SELECT * FROM display_new WHERE user_id = ? AND nure_group = ?', (user_id, nure_group)).fetchall()
            return bool(len(result))

    def add_display(self, user_id, nure_group, subject, status = True):
        with self.connection:
            return self.cursor.execute('INSERT INTO display_new (user_id, nure_group, subject, status) VALUES (?,?,?,?)', (user_id, nure_group, subject, status))

    def update_display(self, user_id, nure_group, subject):
        with self.connection:
            return self.cursor.execute('UPDATE display_new SET status = NOT status WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject))

    def get_display(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT status FROM display_new WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject)).fetchall()
            return result[0][0]

    def get_all_display(self, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT user_id, nure_group FROM display_new WHERE nure_group = ? AND subject = ? AND status = 1', (nure_group, subject)).fetchall()
            return result

    def has_positive_display(self, user_id, nure_group, subject):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM display_new WHERE user_id = ? AND nure_group = ? AND subject = ? AND status = 1',(user_id, nure_group, subject)).fetchall()
            return bool(len(result))

    def delete_display(self, user_id, nure_group, subject):
        with self.connection:
            return self.cursor.execute('DELETE FROM display_new WHERE user_id = ? AND nure_group = ? AND subject = ?', (user_id, nure_group, subject))

    def delete_user(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE FROM display_new WHERE user_id = ?', (user_id,))

    def clear(self):
        with self.connection:
            return self.cursor.execute('DELETE FROM display_new')
