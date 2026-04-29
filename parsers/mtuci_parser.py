import requests
import json
from typing import List
from datetime import datetime, timedelta
from models.lesson import Lesson
from parsers.base_parser import BaseParser

class MTUCIParser(BaseParser):
    def __init__(self):
        self.base_url = "https://mtuci.ru"
        self.ajax_url = "https://mtuci.ru/bitrix/services/main/ajax.php"
        self.sessid = None

    def _get_sessid(self) -> str:
        import re
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        }
        response = requests.get(f"{self.base_url}/time-table/", headers=headers, timeout=10)
        sessid = response.cookies.get('PHPSESSID')
        if sessid:
            return sessid
        match = re.search(r'name="sessid".*?value="([a-f0-9]+)"', response.text)
        if match:
            return match.group(1)
        raise Exception("Failed to get sessid")

    def parse(self, group_name: str, week_type: str = "both") -> List[Lesson]:
        if not self.sessid:
            self.sessid = self._get_sessid()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
        }

        params = {
            'c': 'mtuci:timetable',
            'action': 'getTimetableByValue',
            'mode': 'class'
        }

        now = datetime.now()
        data = {
            'VALUE': group_name.upper().strip(),
            'MONTH': now.month,
            'YEAR': now.year,
            'TYPE': 'group',
            'SITE_ID': 's3',
            'sessid': self.sessid
        }

        response = requests.post(self.ajax_url, params=params, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        json_data = response.json()

        all_lessons = self._json_to_lessons(json_data)

        if week_type == "both":
            return all_lessons

        return self._get_one_week_by_parity(all_lessons, week_type)

    def _json_to_lessons(self, json_data: dict) -> List[Lesson]:
        if json_data.get('status') != 'success':
            raise Exception("API error")

        days_data = json_data.get('data', {}).get('days', {})
        weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

        all_dates = []
        for date_str in days_data.keys():
            try:
                d = datetime.strptime(date_str, "%d.%m.%Y")
                all_dates.append(d)
            except:
                pass

        if all_dates:
            min_date = min(all_dates)
            year = min_date.year
            if min_date.month < 9:
                year -= 1
            semester_start = datetime(year, 9, 1)
        else:
            semester_start = datetime.now().replace(month=9, day=1)

        lessons = []
        for date_str, day_lessons in days_data.items():
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                weekday = weekdays[date_obj.weekday()]
                week_num = (date_obj - semester_start).days // 7
                parity = "odd" if (week_num % 2 == 0) else "even"
            except:
                weekday = "?"
                parity = "both"

            for lesson in day_lessons:
                lessons.append(Lesson(
                    day=weekday,
                    subject=lesson.get('UF_DISCIPLINE', ''),
                    start_time=lesson.get('UF_TIME_START', ''),
                    end_time=lesson.get('UF_TIME_END', ''),
                    date=date_str,
                    week_type=parity
                ))
        return lessons

    def _get_one_week_by_parity(self, lessons: List[Lesson], target_parity: str) -> List[Lesson]:
        weeks = {}
        today = datetime.now().date()

        for lesson in lessons:
            if not lesson.date or lesson.week_type != target_parity:
                continue

            try:
                d = datetime.strptime(lesson.date, "%d.%m.%Y").date()
                monday = d - timedelta(days=d.weekday())
                week_key = monday.isoformat()

                if week_key not in weeks:
                    weeks[week_key] = []
                weeks[week_key].append(lesson)
            except:
                pass

        if not weeks:
            return []

        best_week = None
        best_diff = None

        for week_key in weeks.keys():
            week_date = datetime.strptime(week_key, "%Y-%m-%d").date()
            diff = abs((week_date - today).days)

            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_week = week_key

        return weeks.get(best_week, [])

    def validate(self, lessons: List[Lesson]) -> bool:
        return len(lessons) > 0