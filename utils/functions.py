import re


roman_to_int = {
    None: 0,
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10
}


def split_ach_title(title: str):
    match = re.match(r'^(.*?)(?:\s+(I{1,3}|IV|V|VI{0,3}|IX|X{1,3}))?$', title)
    if match:
        name = match.group(1).strip()
        level = match.group(2) or None
        return name, level
    return title, None  # если не совпало, вернуть всё как имя


def format_achievement(ach, date=None, completed_level: str=None):
    date_str = f"(получено: {date.strftime('%d.%m.%Y')})" if date else ""
    return f"**{ach.name}** {date_str}\n> - {ach.description}\n> _({ach.condition_description})_{'\n> _Выполнено: '+ completed_level + '_' if completed_level else ''}"