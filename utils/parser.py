import requests
import re
from bs4 import BeautifulSoup as BS
from loader import groups, groups_list, week_lectures, notify_lectures
from utils.utilities import datetime_now

def parseApiGroups():
    print("[Updating all groups] Sending request")
    r = requests.get("https://nure-dev.pp.ua/api/groups")
    print("[Updating all groups] Request successful")
    res = r.json()
    for group in res:
        print(f"Група {group['name']} код: {group['id']} додана")
        groups_list.add_group(group['name'], group['id'])

def parseGroup():
    r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:2:2677400761397891::NO#")
    html = BS(r.content, 'lxml')
    result = html.find("div", id="GROUPS_AJAX")
    groups_data_lines = result.find_all("a", style="white-space:nowrap;")
    groups_list.truncate() # Deleting existing groups
    for group_line in groups_data_lines:
        match = re.search(r"\('(.+)',(.+)\)", group_line.get("onclick"))
        group = match.group(1)
        code = match.group(2)
        print(f"{group} - {code}")
        groups_list.add_group(group, code)

class Lecture:
    def __init__(self, index, name, f_type, start_hours, start_minutes, end_hours, end_minutes, name2 = [], f_type2 = "None"):
        self.index = index
        self.name = name
        self.f_type = f_type
        if f_type == "Лк":
            self.type = "Лекція"
        elif f_type == "Пз":
            self.type = "Практичне заняття"
        elif f_type == "Лб":
            self.type = "Лабораторне заняття"
        elif f_type == "Конс":
            self.type = "Консультація"
        else:
            self.type = "Не визначено"

        if f_type2 == "Лк":
            self.type2 = "Лекція"
        elif f_type2 == "Пз":
            self.type2 = "Практичне заняття"
        elif f_type2 == "Лб":
            self.type2 = "Лабораторне заняття"
        elif f_type2 == "Конс":
            self.type2 = "Консультація"
        else:
            self.type2 = "Не визначено"
        self.start_hours = start_hours
        self.start_minutes = start_minutes
        self.end_hours = end_hours
        self.end_minutes = end_minutes
        self.name2 = name2
        self.f_type2 = f_type2

    def startTime(self):
        return self.start_hours + ":" + self.start_minutes

    def endTime(self):
        return self.end_hours + ":" + self.end_minutes

    def set_start_time(self, start_hours, start_minutes):
        self.start_hours = start_hours
        self.start_minutes = start_minutes


def parseWeek(day1, month1, year1, day2, month2, year2, group = "КНТ-22-4"):
    # all_groups = Groups("database.db")
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
            # if current_date == "01.10.2024":
                # if doodoododo:
                #     pairs_test = [["*СГМтА", "Лк"], ["*ФJS", "Пз"], ["ПВСЗД", "Лк"], ["ФВ", "Пз"]]
                #     # pairs_test = [["*СГМтА", "Лк"]]
                #     current_time = datetime_now()
                #     minute = current_time.time().minute + 6
                #     hour = current_time.time().hour
                #     parsed_week["01.10.2024"].append(Lecture("1", pairs_test, "Лк", str(hour), str(minute), "20", "00"))
                #     # parsed_week["30.09.2024"].append(Lecture("1", pairs_test, "Лк", "20", "20", "21", "00"))
                #     # parsed_week["01.10.2024"].append(Lecture("2", [["*ФJS", "Лк"]], "Лк", "22", "20", "23", "00"))
                #
                #     doodoododo = False
            pair_number = row.find('td', class_='left').text
            pair_time = row.find('td', class_='left').find_next_sibling().text
            start = re.search(r'(.+)\s', pair_time).group().replace(" ", "")
            end = re.search(r'\s(.+)', pair_time).group().replace(" ", "")
            start_hours, start_minutes = start.split(':')
            end_hours, end_minutes = end.split(':')

            pairs = row.find_all('a', class_="linktt")
            multiple_pairs = []
            for pair in pairs:
                type = re.search(r'\s(\w+)', pair.text).group().replace(" ", "")
                name = re.search(r'(.+)\s', pair.text).group().replace(" ", "")
                multiple_pairs.append([name, type])
            # print(f"Эмуляция создания объекта: \nmain: {multiple_pairs[0][0]} {multiple_pairs[0][1]}\nothers: {multiple_pairs[1:]}")
            parsed_week[current_date].append(Lecture(pair_number, multiple_pairs, "Лк", start_hours, start_minutes, end_hours, end_minutes))

            # if len(pairs) > 1:
            #     # type1 = re.search(r'\s(\w+)', pairs[0].text).group().replace(" ", "")
            #     # name1 = re.search(r'(.+)\s', pairs[0].text).group().replace(" ", "")
            #     # type2 = re.search(r'\s(\w+)', pairs[1].text).group().replace(" ", "")
            #     # name2 = re.search(r'(.+)\s', pairs[1].text).group().replace(" ", "")
            #     #
            #     # parsed_week[current_date].append(Lecture(pair_number, name1, type1, start_hours, start_minutes, end_hours, end_minutes, name2, type2))
            #     #
            #     # # parsed_week[current_date].append(Lecture(pair_number, name2, type2, start_hours, start_minutes, end_hours, end_minutes))
            #     # print(f"Добавлена двойная пара: {name1} | {name2}")
            #
            #     print("Запуск цикла")
            #     multiple_pairs = []
            #     for pair in pairs:
            #         type = re.search(r'\s(\w+)', pair.text).group().replace(" ", "")
            #         name = re.search(r'(.+)\s', pair.text).group().replace(" ", "")
            #         print(f"Добавлено: {name} {type}")
            #         multiple_pairs.append([name, type])
            #     # print(f"Эмуляция создания объекта: \nmain: {multiple_pairs[0][0]} {multiple_pairs[0][1]}\nothers: {multiple_pairs[1:]}")
            #     parsed_week[current_date].append(Lecture(pair_number, multiple_pairs, "Лк", start_hours, start_minutes, end_hours, end_minutes))
            # # else:
            # #     type = re.search(r'\s(\w+)', pairs[0].text).group().replace(" ", "")
            # #     name = re.search(r'(.+)\s', pairs[0].text).group().replace(" ", "")
            # #     parsed_week[current_date].append(Lecture(pair_number, name, type, start_hours, start_minutes, end_hours, end_minutes))
            # #     print(f"Добавлена пара: {name}")

    # week_lectures[group] = parsed_week
    # notify_lectures[group] = week_lectures[group]["01.10.2024"][1:]

    return parsed_week


def parseSubjects(group = "КНТ-22-4"):
    try:
        # all_groups = Groups("database.db")
        group_code = groups.get_code(group)
        r = requests.get(f"https://cist.nure.ua/ias/app/tt/f?p=778:201:1616752339325756:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.09.2024,31.01.2025,{group_code},0:")
        # if group == "КНТ-22-4":
        #     r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:201:622623529402425:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.09.2023,31.01.2024,10306577,0:")
        # elif group == "ВПВПС-22-3":
        #     r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:201:3627512681037055:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.09.2023,31.01.2024,10284323,0:")
        # elif group == "ІТУ-22-1":
        #     r = requests.get("https://cist.nure.ua/ias/app/tt/f?p=778:201:4698868271516682:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.09.2023,31.01.2024,10306589,0:")
        html = BS(r.content, 'lxml')

        subjects_names_table = html.find("table", class_="footer").find_all("td", class_="name")
        result_subjects = []
        for el in subjects_names_table:
            result_subjects.append(el.text)

        return result_subjects
    except:
        print(f"Error {group}")

def parseDay(day, month, year, group = "КНТ-22-4"):
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
        #print(f"{index[i].text} пара: {subj_name}\n{subj_type}\nЧас: {time[i].text}\n")
        #print(f"{pari[i].index} пара: {pari[i].name}\n{pari[i].type}\nПочаток: {pari[i].start_hours}:{pari[i].start_minutes}\nКінець: {pari[i].end_hours}:{pari[i].end_minutes}\n")

    return lectures