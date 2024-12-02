import re

import requests

from analytics.diagrams import send, PopularSkillDiagramBuilder
from cache import Cache
from database_queries import get_popular_skills
from images import Image
from validation import normalize_string, validate_letters_with_spaces


class BaseDiagramProcessor:
    query = None
    builder_class = None

    def __init__(self, cache: Cache):
        self.cache = cache

    def process(self, profession: str) -> None:
        if profession:
            data_for_diagram, diagram, path = prepare_data(
                profession, self.cache, get_popular_skills,
                PopularSkillDiagramBuilder
            )
            send(diagram, data_for_diagram, path)
            self.cache.save_path_image(profession, path)


class SalaryDiagramProcessor(BaseDiagramProcessor):
    query = get_comparing_skills_with_salary
    builder_class = SkillsSalaryDiagramBuilder


class PopularSkillsDiagramProcessor(BaseDiagramProcessor):
    query = get_popular_skills
    builder_class = PopularSkillDiagramBuilder


def process_of_processing_diagrams(profession: str, request: requests, cache: Cache) -> None:
    if profession:
        data_for_diagram, diagram, path = prepare_data(profession, cache, get_popular_skills,
                                                       PopularSkillDiagramBuilder)
        send(diagram, data_for_diagram, path)
        cache.save_path_image(profession, path)


def prepare_data(profession: str, cache: Cache, func_for_get_data: callable, class_for_draw: callable) -> tuple:
    if profession is not None:
        path = cache.get_pathfile_for_profession(profession)
        if path:
            path = path.decode('utf-8')
        else:
            data_for_diagram = func_for_get_data(profession)
            diagram = class_for_draw()
            path = Image.get_path(profession)
    return data_for_diagram, diagram, path


def get_valid_data(profession) -> str | None:
    try:
        normal_profession = normalize_string(profession)
        valid_profession = validate_letters_with_spaces(normal_profession)
    except ValueError as e:
        return e # ????
    return valid_profession

