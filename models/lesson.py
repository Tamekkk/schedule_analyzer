from dataclasses import dataclass
from typing import Optional

@dataclass
class Lesson:
    day: str
    subject: str
    start_time: str
    end_time: str
    teacher: Optional[str] = None
    room: Optional[str] = None
    lesson_type: Optional[str] = None
    date: Optional[str] = None
    week_type: str = "both"

    def __repr__(self) -> str:
        return f"{self.day} {self.start_time}-{self.end_time} {self.subject}"

    def to_dict(self) -> dict:
        return {
            'day': self.day,
            'subject': self.subject,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'teacher': self.teacher,
            'room': self.room,
            'lesson_type': self.lesson_type,
            'date': self.date,
            'week_type': self.week_type
        }