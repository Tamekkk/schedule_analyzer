from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
from models.lesson import Lesson
from utils.time_utils import to_min, to_str

class ScheduleAnalyzer:
    def __init__(self, lessons: List[Lesson]):
        self.lessons = lessons

    def filter_by_week(self, week_type: str) -> List[Lesson]:
        if week_type == "both":
            return self.lessons.copy()
        return [l for l in self.lessons if l.week_type == week_type or l.week_type == "both"]

    def count_by_day(self, lessons: List[Lesson]) -> Dict[str, int]:
        days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        cnt = Counter(l.day for l in lessons)
        return {d: cnt.get(d, 0) for d in days}

    def get_busiest_day(self, day_counts: Dict[str, int]) -> Tuple[str, int]:
        if not day_counts:
            return ("нет", 0)
        return max(day_counts.items(), key=lambda x: x[1])

    def find_windows(self, lessons: List[Lesson],
                     free_slots: Optional[Dict[str, Tuple[int, int]]] = None,
                     min_duration: int = 30) -> List[Dict]:
        by_day = defaultdict(list)
        for l in lessons:
            by_day[l.day].append(l)

        windows = []
        days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

        for day in days:
            if day not in by_day:
                continue

            day_lessons = sorted(by_day[day], key=lambda x: to_min(x.start_time))

            for i in range(len(day_lessons) - 1):
                curr = day_lessons[i]
                nxt = day_lessons[i + 1]

                curr_end = to_min(curr.end_time)
                nxt_start = to_min(nxt.start_time)
                gap = nxt_start - curr_end

                if gap >= min_duration:
                    win = {
                        'day': day,
                        'start': curr.end_time,
                        'end': nxt.start_time,
                        'duration': gap
                    }

                    if free_slots and day in free_slots:
                        fs_start, fs_end = free_slots[day]
                        if curr_end >= fs_start and nxt_start <= fs_end:
                            windows.append(win)
                    elif not free_slots:
                        windows.append(win)

        return windows

    def find_free_intervals(self, lessons: List[Lesson], free_slots: Dict[str, Tuple[int, int]]) -> List[Dict]:
        by_day = defaultdict(list)
        for l in lessons:
            by_day[l.day].append(l)

        free_intervals = []
        days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

        for day in days:
            if day not in free_slots:
                continue

            fs_start, fs_end = free_slots[day]

            if day not in by_day:
                free_intervals.append({
                    'day': day,
                    'start': to_str(fs_start),
                    'end': to_str(fs_end),
                    'reason': 'весь день свободен'
                })
                continue

            day_lessons = sorted(by_day[day], key=lambda x: to_min(x.start_time))

            has_conflict = False
            for lesson in day_lessons:
                l_start = to_min(lesson.start_time)
                l_end = to_min(lesson.end_time)
                if not (l_end <= fs_start or l_start >= fs_end):
                    has_conflict = True
                    break

            if not has_conflict:
                free_intervals.append({
                    'day': day,
                    'start': to_str(fs_start),
                    'end': to_str(fs_end),
                    'reason': 'нет пар'
                })

        return free_intervals

    def get_statistics(self, lessons: List[Lesson]) -> Dict:
        day_counts = self.count_by_day(lessons)
        busiest_day, busiest_cnt = self.get_busiest_day(day_counts)
        windows = self.find_windows(lessons)

        return {
            'total': len(lessons),
            'day_counts': day_counts,
            'busiest_day': busiest_day,
            'busiest_count': busiest_cnt,
            'windows': windows,
            'windows_count': len(windows)
        }