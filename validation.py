import re

class NullError(Exception):
    pass


def normalize_string(string: str | None) -> str | None:
    if string is not None and len(string) > 0:
        return string.strip()
    raise NullError(f'Строка должна быть заполнена: {string}')


def validate_letters_with_spaces(string: str) -> str:
    if re.fullmatch(r"[A-Za-zА-Яа-яЁё ,]+", string):
        return string
    raise ValueError(f"Строка должна содержать только буквы и пробелы: '{string}'")


def validate_letters_only(string: str) -> str:
    if string.isalpha():
        return string
    raise ValueError(f"Строка должна содержать только буквы: '{string}'")


def validate_digits_only(string: str) -> str:
    if string.isdigit():
        return string
    raise ValueError(f"Строка должна содержать только цифры: '{string}'")


def is_positive_number(number: int | float) -> int | float:
    if int(number) > 0:
        return number
    raise ValueError(f'Число должно быть положительным {number}')
