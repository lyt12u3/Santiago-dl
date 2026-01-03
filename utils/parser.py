from datetime import datetime

import requests
import re
from bs4 import BeautifulSoup as BS
from loader import groups, groups_list, week_lectures, notify_lectures
from utils.utilities import datetime_now, debug

def parseApiGroups():
    print("[Updating all groups] Sending request")
    r = requests.get("https://nure-dev.pp.ua/api/groups")
    print("[Updating all groups] Request successful")
    res = r.json()
    for group in res:
        print(f"Група {group['name']} код: {group['id']} додана")
        groups_list.add_group(group['name'], group['id'])


def parse_faculties():
    faculties = []
    try:
        r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:2:371574995017904::NO:::#")
        html = BS(r.content.decode('windows-1251'), 'lxml')
        div = html.find("div", id="GROUPS_AJAX")
        table = div.find_all("table", class_="htmldbTabbedNavigationList")
        result_a = table[0].find_all("a")
        for el in result_a:
            try:
                name = el.text
                onclick = el.get('onclick')
                number = re.search('\((\d+)\)', onclick)
                faculties.append([name, number.group(1)])
            except Exception as e:
                print(f"Error during processing faculties: {e}")
    except requests.RequestException as e:
        print(f"Error during request faculties: {e}")
    except Exception as e:
        print(f"Error parsing faculties: {e}")
    return faculties


def parseGroup():
    faculties = parse_faculties()
    groups_list.truncate()
    for fac in faculties:
        print(f"Processing faculty: {fac[0]}")
        r = requests.get(f"https://cist.nure.ua/ias/app/tt/WEB_IAS_TT_AJX_GROUPS?p_id_fac={fac[1]}")
        html = BS(r.content, 'lxml')
        # result = html.find("div", id="GROUPS_AJAX")
        groups_data_lines = html.find_all("a", style="white-space:nowrap;")
        for group_line in groups_data_lines:
            match = re.search(r"\('(.+)',(.+)\)", group_line.get("onclick"))
            group = match.group(1)
            code = match.group(2)
            print(f"{group} - {code}")
            groups_list.add_group(group, code)


def parseGroup_old():
    r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:2:2677400761397891::NO#")
    html = BS(r.content, 'lxml')
    result = html.find("div", id="GROUPS_AJAX")
    groups_data_lines = result.find_all("a", style="white-space:nowrap;")
    groups_list.truncate()  # Deleting existing groups
    for group_line in groups_data_lines:
        match = re.search(r"\('(.+)',(.+)\)", group_line.get("onclick"))
        group = match.group(1)
        code = match.group(2)
        print(f"{group} - {code}")
        groups_list.add_group(group, code)


class Lecture:
    def __init__(self, index, info, start_hours, start_minutes, end_hours, end_minutes):
        self.index = index
        self.info = info
        self.start_hours = start_hours
        self.start_minutes = start_minutes
        self.end_hours = end_hours
        self.end_minutes = end_minutes
        # self.f_type = f_type
        # if f_type == "Лк":
        #     self.type = "Лекція"
        # elif f_type == "Пз":
        #     self.type = "Практичне заняття"
        # elif f_type == "Лб":
        #     self.type = "Лабораторне заняття"
        # elif f_type == "Конс":
        #     self.type = "Консультація"
        # else:
        #     self.type = "Не визначено"


    def startTime(self):
        return self.start_hours + ":" + self.start_minutes

    def endTime(self):
        return self.end_hours + ":" + self.end_minutes

    def set_start_time(self, start_hours, start_minutes):
        self.start_hours = start_hours
        self.start_minutes = start_minutes

class LectureTeacher:
    def __init__(self, index, teacher, name, type, group, start_hours, start_minutes, end_hours, end_minutes):
        self.index = index
        self.teacher = teacher
        self.name = name
        self.type = type
        self.group = group
        self.start_hours = start_hours
        self.start_minutes = start_minutes
        self.end_hours = end_hours
        self.end_minutes = end_minutes


    def startTime(self):
        return self.start_hours + ":" + self.start_minutes

    def endTime(self):
        return self.end_hours + ":" + self.end_minutes

    def set_start_time(self, start_hours, start_minutes):
        self.start_hours = start_hours
        self.start_minutes = start_minutes

def parseWeek(day1, month1, year1, day2, month2, year2, group="КНТ-22-4"):
    group_code = groups.get_code(group)
    r = requests.get(
        f"https://cist.nure.ua/ias/app/tt/f?p=778:201:1616752339325756:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{day1}.{month1}.{year1},{day2}.{month2}.{year2},{group_code},0:")
    html = BS(r.content, 'lxml')
    rows = html.select('table.MainTT tr')[1:]

    current_day = None
    current_date = None
    parsed_week = {}

    # doodoododo = True

    for row in rows:
        day_element = row.find('td', class_='date', colspan=True)
        date_element = row.find('td', class_='date', colspan=False)
        if day_element and date_element:
            current_day = day_element.text
            current_date = date_element.text
            parsed_week[current_date] = [current_day]
        else:
            pair_number = row.find('td', class_='left').text
            pair_time = row.find('td', class_='left').find_next_sibling().text
            start = re.search(r'(.+)\s', pair_time).group().replace(" ", "")
            end = re.search(r'\s(.+)', pair_time).group().replace(" ", "")
            start_hours, start_minutes = start.split(':')
            end_hours, end_minutes = end.split(':')

            pairs = row.find_all('a', class_="linktt")
            multiple_pairs = []
            for pair in pairs:
                type = re.search(r'\s(\w+)$', pair.text).group()[1:]
                name = re.search(r'(.+)\s', pair.text).group()[:-1]
                multiple_pairs.append([name, type])
            parsed_week[current_date].append(Lecture(pair_number, multiple_pairs, start_hours, start_minutes, end_hours, end_minutes))
    # print(parsed_week)
    return parsed_week


def get_semester_dates():
    try:
        r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:2:371574995017904::NO:::#")
        html = BS(r.content, 'lxml')
        datepickers = html.find_all('td', class_='datepicker')
        start_date = datepickers[0].find_all('input')[1].get('value')
        end_date = datepickers[1].find_all('input')[1].get('value')
        return start_date, end_date
    except Exception as e:
        print(f"Error getting semester dates: {e.args[0]}")


def parseSubjects(group="КНТ-22-4", start_date=None, end_date=None):
    try:
        if not start_date and not end_date:
            debug("Subjects updating: parsing start and end dates...")
            start_date, end_date = get_semester_dates()
            debug("Subjects updating: parsing subjects...")
        group_code = groups.get_code(group)
        r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:527954707314034:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{start_date},{end_date},{group_code},0:")
        html = BS(r.content, 'lxml')

        subjects_names_table = html.find("table", class_="footer").find_all("td", class_="name")
        result_subjects = []
        for el in subjects_names_table:
            result_subjects.append(el.text)

        return result_subjects
    except Exception as e:
        print(f"Error {group}: {e.args[0]}")

def parseDay(day, month, year, group="КНТ-22-4"):
    # all_groups = Groups("database.db")
    group_code = groups.get_code(group)
    r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:1616752339325756:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{day}.{month}.{year},{day}.{month}.{year},{group_code},0:")
    # if group == "КНТ-22-4":
    #     r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:1616752339325756:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{day}.{month}.{year},{day}.{month}.{year},10306577,0:")
    # elif group == "ВПВПС-22-3":
    #     r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:4044290297149793:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{day}.{month}.{year},{day}.{month}.{year},10284323,0:")
    # elif group == "ІТУ-22-1":
    #     r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:3144824475606018:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{day}.{month}.{year},{day}.{month}.{year},10306589,0:")
    html = BS(r.content, 'lxml')

    index = html.find("table", class_="MainTT").find_all("td", class_="left", string=re.compile(r'^\d{1}$'))
    time = html.find("table", class_="MainTT").find_all("td", class_="left", string=re.compile(r':'))
    subj = html.find("table", class_="MainTT").find_all("a", class_="linktt")

    # if len(index) != 0:
    #     print("Пар сегодня:", len(index))
    # else:
    #     print("Пар сегодня нет")

    lectures = []

    for i in range(len(subj)):
        type = re.search(r'\s(\w+)', subj[i].text).group().replace(" ", "")
        name = re.search(r'(.+)\s', subj[i].text).group().replace(" ", "")
        start = re.search(r'(.+)\s', time[i].text).group().replace(" ", "")
        end = re.search(r'\s(.+)', time[i].text).group().replace(" ", "")
        start_hours, start_minutes = start.split(':')
        end_hours, end_minutes = end.split(':')
        # start_hours = re.search(r'(\d+):', start).group().replace(":", "")
        # start_minutes = re.search(r':(\d+)', start).group().replace(":", "")
        # end_hours = re.search(r'(\d+):', end).group().replace(":", "")
        # end_minutes = re.search(r':(\d+)', end).group().replace(":", "")
        lectures.append(Lecture(index[i].text, name, type, start_hours, start_minutes, end_hours, end_minutes))
        # print(f"{index[i].text} пара: {subj_name}\n{subj_type}\nЧас: {time[i].text}\n")
        # print(f"{pari[i].index} пара: {pari[i].name}\n{pari[i].type}\nПочаток: {pari[i].start_hours}:{pari[i].start_minutes}\nКінець: {pari[i].end_hours}:{pari[i].end_minutes}\n")

    return lectures


def parse_kafedras():
    kafedras = []
    try:
        r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:4:1011919354201228::NO:::#")
        html = BS(r.content.decode('windows-1251'), 'lxml')
        div = html.find("div", id="TEACHS_AJAX")
        table = div.find_all("table", class_="htmldbTabbedNavigationList")
        result_a = table[1].find_all("a")
        for el in result_a:
            try:
                name = el.text.replace("Кафедра ", "")
                onclick = el.get('onclick')
                number = re.search(',(.+)\)', onclick)
                kafedras.append([name, number.group(1)])
            except Exception as e:
                print(f"Error during processing kafedras: {e}")
    except requests.RequestException as e:
        print(f"Error during request kafedras: {e}")
    except Exception as e:
        print(f"Error parsing kafedras: {e}")
    return kafedras


def parse_teachers(kaf,):
    teachers = []
    try:
        link = f"https://cist.nure.ua/ias/app/tt/WEB_IAS_TT_AJX_TEACHS?p_id_fac=95&p_id_kaf={kaf}"
        r = requests.get(link)
        html = BS(r.content.decode('windows-1251'), 'lxml')
        result = html.find("table", class_="t13Standard")
        teachers_arr = result.find_all("td", class_="t13datatop")
        for teacher in teachers_arr:
            try:
                line = teacher.find("a")
                teacher_info_raw = line.get('onclick')
                search = re.search("\('(.+)',(.+)\)", teacher_info_raw)
                name, code = search.group(1), search.group(2)
                teachers.append([name, code])
            except:
                pass
    except requests.RequestException as e:
        print(f"Error during request teachers: {e}")
    except Exception as e:
        print(f"Error parsing teachers: {e}")
    return teachers


def parse_all_teachers():
    all_teachers = []
    kafedras = parse_kafedras()
    for kafedra in kafedras:
        debug(f"Processing kafedra #{kafedra[1]}...")
        teachers = parse_teachers(kafedra[1])
        for teacher in teachers:
            all_teachers.append(teacher)
    return all_teachers

def parse_teacher_week(day1, month1, year1, day2, month2, year2, teacher):
    link = f"https://cist.nure.ua/ias/app/tt/f?p=778:202:611417407963254:::202:P202_FIRST_DATE,P202_LAST_DATE,P202_SOTR,P202_KAF:{day1}.{month1}.{year1},{day2}.{month2}.{year2},{teacher},0:"
    r = requests.get(link)
    html = BS(r.content, 'lxml')
    rows = html.select('table.MainTT tr')[1:]

    current_day = None
    current_date = None
    parsed_week = {}


    for row in rows:
        day_element = row.find('td', class_='date', colspan=True)
        date_element = row.find('td', class_='date', colspan=False)
        if day_element and date_element:
            current_day = day_element.text
            current_date = date_element.text
            parsed_week[current_date] = [current_day]
        else:
            pair_number = row.find('td', class_='left').text

            pair_time = row.find('td', class_='left').find_next_sibling().text
            start = re.search(r'(.+)\s', pair_time).group().replace(" ", "")
            end = re.search(r'\s(.+)', pair_time).group().replace(" ", "")
            start_hours, start_minutes = start.split(':')
            end_hours, end_minutes = end.split(':')

            pair_data = row.find('td', bgcolor=True).getText()
            name, type, app, group = pair_data[1:-1].split(" ")
            group = group.replace(name, "")

            parsed_week[current_date].append(LectureTeacher(pair_number, teacher, name, type, group, start_hours, start_minutes, end_hours, end_minutes))
            # print(f"Name |{name}| type |{type}| app |{app}| group |{group}|")
    return parsed_week

def parseYear(group="КНТ-22-4", start_date=None, end_date=None):
    try:
        if not start_date and not end_date:
            debug("Subjects updating: parsing start and end dates...")
            start_date, end_date = get_semester_dates()
            debug("Subjects updating: parsing subjects...")
        group_code = groups.get_code(group)
        # group_code = "10306577"
        URL = f"https://cist.nure.ua/ias/app/tt/f?p=778:201:527954707314034:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:{start_date},{end_date},{group_code},0:"
        r = requests.get(URL)
        html = BS(r.content, 'lxml')
        table = html.select('table.MainTT tr')[1:]

        schedule = []

        year = {}

        for item in table:
            debug("ITEM: ============")
            # print(item)
            lectures_check = item.find('td', class_='left')
            if lectures_check is None:
                debug("PARSING DATES...")
                elements = item.find_all('td', class_='date')
                weekday = elements[0].text
                year[weekday] = {}
                dates_unformatted = elements[1:]
                dates = []
                for obj in dates_unformatted:
                    dates.append(obj.text)
                    year[weekday][obj.text] = []
                # print(f"DAY: {weekday}\nINFO: {dates}")
                debug("DATES PARSED SUCCESSFULLY")
            else:
                debug("LECTURES DETECTED, PARSING...")
                index = item.find('td').text
                time = item.find('td').find_next_sibling().text
                debug(f"{index}: {time}")
                weekdays = list(year.keys())
                currentWeekday = weekdays[-1]
                debug(f"Parsing into: {currentWeekday}")
                items = item.find_all('td')[2:]

                iterator = 0
                for block in items:
                    dates = list(year[currentWeekday].keys())

                    a_tags = block.find_all("a")
                    if a_tags:
                        info = []
                        for pair in a_tags:
                            type = re.search(r'\s(\w+)$', pair.text).group()[1:]
                            name = re.search(r'(.+)\s', pair.text).group()[:-1]
                            info.append([name, type])
                        start = re.search(r'(.+)\s', time).group().replace(" ", "")
                        end = re.search(r'\s(.+)', time).group().replace(" ", "")
                        start_hours, start_minutes = start.split(':')
                        end_hours, end_minutes = end.split(':')

                        colspan = block.get('colspan')
                        if colspan:
                            # print(f"Multilecture detected with width = {colspan}")
                            start_day = iterator
                            end_day = iterator + int(colspan)
                            for day_num in range(start_day, end_day):
                                debug(f"{dates[day_num]}: Lecture detected: {info}")
                                lect = Lecture(index, info, start_hours, start_minutes, end_hours, end_minutes)
                                year[currentWeekday][dates[day_num]].append(lect)
                            iterator = iterator + int(colspan)
                        else:
                            lect = Lecture(index, info, start_hours, start_minutes, end_hours, end_minutes)
                            year[currentWeekday][dates[iterator]].append(lect)
                            debug(f"{dates[iterator]}: Single lecture detected: {info}")
                            iterator = iterator + 1
                    else:
                        debug(f"{dates[iterator]}")
                        iterator = iterator + 1

        return normalize_year(year)
    except Exception as e:
        print(f"Error {group}: {e.args[0]}")

def normalize_year(old_year):
    formatted = {}
    for weekday in old_year:
        for date in old_year[weekday]:
            new_date = old_year[weekday][date]
            new_date.insert(0, weekday)
            formatted[date] = new_date

    formatted = dict(sorted(formatted.items(),key=lambda item: datetime.strptime(item[0], "%d.%m.%Y")))

    return formatted