from analytics.diagrams import send, PopularSkillDiagramBuilder, SkillsSalaryDiagramBuilder
from cache import Cache, CacheSessionPathImage
from database_queries import get_popular_skills, get_comparing_skills_with_salary
from images import Image


class BaseDiagramProcessor:
    query = None
    builder_class = None

    def __init__(self, cache: Cache):
        self.cache = cache

    def process(self, profession: str) -> str:
        data_for_diagram, diagram, path = prepare_data(
            profession, self.cache, self.query,
            self.builder_class
        )
        send(diagram, data_for_diagram, path)
        self.cache.save_path_image(profession, path)
        return str(path)


class SalaryDiagramProcessor(BaseDiagramProcessor):
    query = staticmethod(get_comparing_skills_with_salary)
    builder_class = SkillsSalaryDiagramBuilder


class PopularSkillsDiagramProcessor(BaseDiagramProcessor):
    query = staticmethod(get_popular_skills)
    builder_class = PopularSkillDiagramBuilder


def prepare_data(profession: str, cache: CacheSessionPathImage, func_for_get_data: callable,
                 class_for_draw: callable) -> tuple:
    path = cache.get_pathfile_for_profession(profession)
    if path:
        path = path.decode('utf-8')
    else:
        data_for_diagram = func_for_get_data(profession)
        diagram = class_for_draw()
        path = Image.get_path(profession)
    return data_for_diagram, diagram, path
