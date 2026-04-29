# Доп. функции работы со временем
def to_min(t: str) -> int:
    # время в минуты
    try:
        h, m = map(int, t.split(':'))
        return h * 60 + m
    except:
        return 0

# минуты в строку времени
def to_str(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"