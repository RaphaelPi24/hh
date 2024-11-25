import os
import re
from typing import Optional

import requests

from analytics.data_for_diagram import get_popular_skills
from analytics.diagrams import send, PopularSkillDiagramBuilder
from images import Image
from vacancy_service import Cache


def process_of_processing_diagrams(input_name: str, request: requests, cache: Cache) -> None:



def get_valid_data(profession) -> Optional[str]:
    if profession is not None and len(profession) > 0:
        profession = profession.strip()
        if re.fullmatch(r"[A-Za-zА-Яа-яЁё ]+", profession):
            return profession
    return None


def prepare_data(profession: str, cache: Cache, func_for_get_data: callable, class_for_draw: callable) -> tuple:
    if profession is not None:
        path = cache.get_pathfile_for_profession(profession)
        if path:
            path = path.decode('utf-8')
        else:
            data_for_diagram = func_for_get_data(profession)
            diagram = class_for_draw()
            path = Image().get_path(profession)
    return data_for_diagram, diagram, path
