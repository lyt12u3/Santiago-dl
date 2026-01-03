import requests
import re
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
from utils.utilities import debug

class Lecture:
    def __init__(self, index, info, start_hours, start_minutes, end_hours, end_minutes):
        self.index = index
        self.info = info
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


URL = "https://cist.nure.ua/ias/app/tt/f?p=778:201:994904331548970:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.09.2025,31.01.2026,10889681,0:"

def parseYear():
    r = requests.get(URL)
    html = BS(r.content, 'lxml')
    table = html.select('table.MainTT tr')[1:]

    group = "КНТ-22-4"
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

                    lect = Lecture(index, info, start_hours, start_minutes, end_hours, end_minutes)

                    colspan = block.get('colspan')
                    if colspan:
                        # print(f"Multilecture detected with width = {colspan}")
                        start_day = iterator
                        end_day = iterator + int(colspan)
                        for day_num in range(start_day, end_day):
                            debug(f"{dates[day_num]}: Lecture detected: {info}")
                            year[currentWeekday][dates[day_num]].append(lect)
                        iterator = iterator + int(colspan)
                    else:
                        year[currentWeekday][dates[iterator]].append(lect)
                        debug(f"{dates[iterator]}: Single lecture detected: {info}")
                        iterator = iterator + 1
                else:
                    debug(f"{dates[iterator]}")
                    iterator = iterator + 1

    return normalize_year(year)

def normalize_year(old_year):
    formatted = {}
    for weekday in old_year:
        for date in old_year[weekday]:
            new_date = old_year[weekday][date]
            new_date.insert(0, weekday)
            formatted[date] = new_date

    formatted = dict(sorted(formatted.items(),key=lambda item: datetime.strptime(item[0], "%d.%m.%Y")))

    return formatted


if __name__ == "__main__":
    print("execution...")
    year = {}
    year["КНТ-22-4"] = parseYear()
    print(year)

