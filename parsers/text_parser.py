import re
from typing import List
from models.lesson import Lesson
from parsers.base_parser import BaseParser

class TextParser(BaseParser):
    def parse(self, text: str) -> List[Lesson]:
        lessons = []

        # паттерны  строк
        patterns = [
            # ДЕНЬ ЧЧ:ММ-ЧЧ:ММ ПРЕДМЕТ
            (r'([ПНВТСРЧТПТСБВС]{2})\s+(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\s+(.+?)(?:\n|$)',
             lambda m: (m[1], m[2], m[3], m[4])),
            # ЧЧ:ММ-ЧЧ:ММ ПРЕДМЕТ (ДЕНЬ)
            (r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\s+(.+?)\s*\(([ПНВТСРЧТПТСБВС]{2})\)',
             lambda m: (m[4], m[1], m[2], m[3])),
        ]

        lines = text.split('\n')

        # обработка строк
        for line in lines:
            for pattern, extractor in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    day, start, end, subject = extractor(match)

                    # очистка предмета
                    subject = subject.strip()
                    subject = re.sub(r'\([^)]*\)', '', subject)
                    subject = re.sub(r'ауд\.\s*\d+', '', subject, flags=re.IGNORECASE)
                    subject = subject.split(',')[0].strip()
                    subject = subject[:100]

                    if subject and len(subject) > 2:
                        lessons.append(Lesson(
                            day=day.upper(),
                            start_time=start,
                            end_time=end,
                            subject=subject,
                            week_type="both"
                        ))
                    break

        return lessons

    def validate(self, lessons: List[Lesson]) -> bool:
        return len(lessons) > 0