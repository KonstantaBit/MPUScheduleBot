
import json
from icalendar import Calendar, Event, vText
import requests
from datetime import datetime, timedelta
import locale

lecture_schedule = {
    '1': timedelta(hours=9),
    '2': timedelta(hours=10, minutes=40),
    '3': timedelta(hours=12, minutes=20),
    '4': timedelta(hours=14, minutes=30),
    '5': timedelta(hours=16, minutes=10),
    '6': timedelta(hours=17, minutes=50),
    '7': timedelta(hours=19, minutes=30),
}


def get_json(group_number: str, is_session: bool = False) -> (int, dict):
    """
    Status codes:
    0 - OK
    1 - Server error
    2 - Group not found
    3 - JSON decode error
    """
    headers = {
        'Referer': 'https://rasp.dmami.ru/',
    }

    params = {
        'group': group_number,
        'session': int(is_session),
    }

    response = requests.get('https://rasp.dmami.ru/site/group', params=params, headers=headers)

    if response.status_code != 200:
        return (1,)
    if group_number not in requests.get('https://rasp.dmami.ru/').text:
        return (2,)
    try:
        data = response.json()
    except json.JSONDecodeError:
        return (3,)
    return 0, data


def get_schedule(json_data: dict) -> Calendar:
    calendar = Calendar()
    for week_day in json_data['grid']:
        for lecture_number in json_data['grid'][week_day]:
            for lecture in json_data['grid'][week_day][lecture_number]:
                df = datetime.strptime(lecture['df'], '%Y-%m-%d')  # Начало лекций
                dt = datetime.strptime(lecture['dt'], '%Y-%m-%d')  # Конец лекций
                subject = lecture['sbj']  # Дисциплина
                teacher = lecture['teacher']  # Преподаватель
                location = lecture['location']  # Локация
                place = lecture['auditories'][0]['title']  # Аудитория
                type_lecture = lecture['type']  # Тип пары

                if df.weekday() <= int(week_day) - 1:
                    inc_date = int(week_day) - 1 - df.weekday()
                else:
                    inc_date = 7 - df.weekday() - 1 + int(week_day)

                if "href" in place:
                    place = place[place.find("https"): place.find('target') - 2]

                dtstart = df + timedelta(days=inc_date) + lecture_schedule[lecture_number]
                dtend = dtstart + timedelta(hours=1, minutes=30)

                event = Event()

                event.add('summary', vText(subject, encoding='utf-8'))
                event.add('dtstart', dtstart)
                event.add('dtend', dtend)
                event.add('rrule', {'freq': 'weekly', 'interval': 1, 'until': dt})
                event.add('location', vText(f'{place} {location}', encoding='utf-8'))
                event.add('description', vText(f'{type_lecture}; {teacher}', encoding='utf-8'))
                calendar.add_component(event)
    return calendar


def get_session_schedule(json_data: dict) -> Calendar:
    calendar = Calendar()
    for week_day in json_data['grid']:
        for lecture_number in json_data['grid'][week_day]:
            for lecture in json_data['grid'][week_day][lecture_number]:
                locale.setlocale(locale.LC_ALL, "")
                dts = datetime.strptime(lecture['dts'], '%d %b %Y') + lecture_schedule[lecture_number]  # Время экзамена
                dte = dts + timedelta(hours=1, minutes=30)
                subject = lecture['sbj']  # Дисциплина
                teacher = lecture['teacher']  # Преподаватель
                type_lecture = lecture['type']  # Тип пары

                event = Event()

                event.add('summary', vText(f'{subject} ({type_lecture})', encoding='utf-8'))
                event.add('dtstart', dts)
                event.add('dtend', dte)
                event.add('description', vText(teacher, encoding='utf-8'))
                calendar.add_component(event)

    return calendar
