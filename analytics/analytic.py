from analytics.diagrams import send, PopularSkillDiagramBuilder, SkillsSalaryDiagramBuilder
from cache import CacheSession, Cache, CacheSessionPathImage
from database_queries import get_popular_skills, get_comparing_skills_with_salary
from images import Image
from validation import normalize_string, validate_letters_with_spaces, validate_digits_only, is_positive_number


class BaseDiagramProcessor:
    query = None
    builder_class = None

    def __init__(self, cache: Cache):
        self.cache = cache
        self.query = None
        self.builder_class = None  # надо или не надо?

    def process(self, profession: str) -> None:
        data_for_diagram, diagram, path = prepare_data(
            profession, self.cache, self.query,
            self.builder_class
        )
        send(diagram, data_for_diagram, path)
        self.cache.save_path_image(profession, path)


class SalaryDiagramProcessor(BaseDiagramProcessor):
    query = get_comparing_skills_with_salary
    builder_class = SkillsSalaryDiagramBuilder


class PopularSkillsDiagramProcessor(BaseDiagramProcessor):
    query = get_popular_skills
    builder_class = PopularSkillDiagramBuilder


def prepare_data(profession: str, cache: CacheSessionPathImage, func_for_get_data: callable,
                 class_for_draw: callable) -> tuple:
    if profession is not None:
        path = cache.get_pathfile_for_profession(profession)
        if path:
            path = path.decode('utf-8')
        else:
            data_for_diagram = func_for_get_data(profession)
            diagram = class_for_draw()
            path = Image.get_path(profession)
    return data_for_diagram, diagram, path


def get_valid_data(profession, title, cache_session) -> str | None:
    try:
        normal_profession = normalize_string(profession)
        valid_profession = validate_letters_with_spaces(normal_profession)
    except ValueError as e:
        valid_profession = None
    return valid_profession


# свой класс формы для каждой страницы
def process_timer(timer: str, cache_session: CacheSession, title: str) -> tuple:
    try:
        timer_digit = validate_digits_only(timer)
        timer_digit = int(timer_digit)  # думал что здесь это команда лишняя
        positive_number_timer = is_positive_number(timer_digit)
    except ValueError as e:
        cache_session.set_message(title, f'Таймер должен быть положительным числом {e}')
        positive_number_timer = timer_digit = None  # калечно
    return positive_number_timer, timer_digit


