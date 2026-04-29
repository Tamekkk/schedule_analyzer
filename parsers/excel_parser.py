import pandas as pd
from typing import List
from models.lesson import Lesson
from parsers.base_parser import BaseParser

class ExcelParser(BaseParser):
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']

    def parse(self, file_path: str) -> List[Lesson]:
        lessons = []

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)

        columns = df.columns.tolist()

        # Поиск по названиям
        day_col = self._find_column(columns, ['день', 'day', 'День'])
        subject_col = self._find_column(columns, ['предмет', 'subject', 'Предмет', 'дисциплина'])
        start_col = self._find_column(columns, ['начало', 'start', 'Начало', 'время начала'])
        end_col = self._find_column(columns, ['конец', 'end', 'Конец', 'время окончания'])

        # Если не нашли берем по позициям
        if not day_col and len(columns) > 0:
            day_col = columns[0]
        if not subject_col and len(columns) > 1:
            subject_col = columns[1]
        if not start_col and len(columns) > 2:
            start_col = columns[2]
        if not end_col and len(columns) > 3:
            end_col = columns[3]

        # Парсинг строк
        for _, row in df.iterrows():
            try:
                day = str(row[day_col]).strip() if day_col else ''
                subject = str(row[subject_col]).strip() if subject_col else ''
                start = str(row[start_col]).strip() if start_col else ''
                end = str(row[end_col]).strip() if end_col else ''

                day = self._normalize_day(day)

                if day and subject and start and end:
                    lessons.append(Lesson(
                        day=day,
                        subject=subject,
                        start_time=self._normalize_time(start),
                        end_time=self._normalize_time(end),
                        week_type="both"
                    ))
            except:
                continue

        return lessons

    # Поиск колонки по вариантам названия
    def _find_column(self, columns: List[str], variants: List[str]) -> str:
        for col in columns:
            for variant in variants:
                if variant.lower() in str(col).lower():
                    return col
        return None

    def _normalize_day(self, day: str) -> str:
        day_map = {
            'пн': 'ПН', 'понедельник': 'ПН',
            'вт': 'ВТ', 'вторник': 'ВТ',
            'ср': 'СР', 'среда': 'СР',
            'чт': 'ЧТ', 'четверг': 'ЧТ',
            'пт': 'ПТ', 'пятница': 'ПТ',
            'сб': 'СБ', 'суббота': 'СБ',
            'вс': 'ВС', 'воскресенье': 'ВС'
        }
        return day_map.get(day.lower(), day.upper())

    def _normalize_time(self, time_str: str) -> str:
        # Нормализация формата времени
        import re
        match = re.search(r'(\d{1,2}):(\d{2})', str(time_str))
        if match:
            return f"{int(match.group(1)):02d}:{match.group(2)}"
        return time_str

    def validate(self, lessons: List[Lesson]) -> bool:
        return len(lessons) > 0