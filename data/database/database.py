import sqlite3

class Database:
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