import hashlib
import json
import re
from pathlib import Path
from typing import Optional

from redis import Redis
from images import Image


# Optional - для значений вместе c None
class Form:
    errors: list[str] = []

    def __init__(self, form: dict) -> None:
        self.form = form
        self.select: str | None = self.get_search_type()
        self.full_search_query: Optional[str] = self.get_full_search_query()
        self.salary_from: Optional[str] = self.get_salary('salary_from')
        self.salary_to: Optional[str] = self.get_salary('salary_to')
        self.city: Optional[str] = self.get_city()
        self.company: Optional[str] = self.get_company()
        self.remote: Optional[bool] = self.get_remote()

    def get_search_type(self) -> Optional[str]:
        select: Optional[str] = self.form.get('search-type')
        if select in {'title', 'skill'}:
            return select
        self.errors.append(f'No correct >select< {select}')
        return None

    def get_full_search_query(self) -> Optional[str]:
        full_search_query = self.form.get('main_query', '').strip()
        if re.fullmatch(r"[A-Za-zА-Яа-яЁё ]+", full_search_query):
            return full_search_query
        self.errors.append(f'No correct >full_search_query< {full_search_query}')
        return None

    def get_salary(self, field_name: str) -> Optional[str]:
        salary: Optional[str] = self.form.get(field_name)
        if salary and len(salary) > 0:
            if salary.strip().isdigit():
                return salary.strip()
            else:
                self.errors.append(f'No correct >{field_name}< {salary}')
        return None

    def get_city(self) -> Optional[str]:
        city: Optional[str] = self.form.get('city')
        if city and len(city) > 0:
            city = city.strip()
            if city.isalpha():
                return city
            else:
                self.errors.append(f'No correct >city< {city}')
        return None

    def get_company(self) -> Optional[str]:
        company: Optional[str] = self.form.get('company')
        if company and len(company) > 0:
            return company.strip()
        return None

    def get_remote(self) -> Optional[bool]:
        remote: Optional[str] = self.form.get('remote')
        if remote == 'on':
            return True
        return None


class Cache:
    """
    Ключ - хэш из кучи параметров.
    Значение - путь с именем диаграммы.
    """
    time_cache_images = 60
    redis_client: Redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)
    names_cache: list[str] = []

    def get_pathfile_for_profession(self, profession: str) -> str:
        if profession:
            path = self.redis_client.hget('user:1000', profession)
            return path

    def get_last_entry(self) -> Optional[str]:
        title = self.redis_client.hget('user:1000', 'diagram')
        path = self.get_pathfile_for_profession(title)
        if path is None:
            path = Image().get_path(title)
        return path

    def save_path_image(self, name : str,  path : str) -> None:
        if isinstance(path, Path):
            path = str(path)
        self.redis_client.setex(name, self.time_cache_images, path)
        self.set_message('diagram', name)

    def get_manual_collection(self) -> Optional[str]:
        message = self.redis_client.hget('user:1000', 'manual_collection')
        if message is not None:
            self.redis_client.hdel('user:1000', 'manual_collection')
        return message

    def get_auto_collection(self) -> Optional[str]:
        values = self.redis_client.hkeys('user:1000')
        if 'finish_autocollection' in values:
            self.redis_client.hdel('user:1000', 'start_autocollection')
            message = self.redis_client.hget('user:1000', 'finish_autocollection')
            if message is not None:
                self.redis_client.hdel('user:1000', 'finish_autocollection')
        elif 'start_autocollection' in values:
            message = self.redis_client.hget('user:1000', 'start_autocollection')
        else:
            message = None
        return message

    def get_delete_images(self) -> Optional[str]:
        values = self.redis_client.hkeys('user:1000')
        if 'finish_delete_images' in values:
            self.redis_client.hdel('user:1000', 'start_delete_images')
            message = self.redis_client.hget('user:1000', 'finish_delete_images')
            if message is not None:
                self.redis_client.hdel('user:1000', 'finish_delete_images')
        elif 'start_delete_images' in values:
            message = self.redis_client.hget('user:1000', 'start_delete_images')
        else:
            message = None
        return message

    def set_message(self, key: str, value: str) -> None:
        self.redis_client.hset('user:1000', key, value)

        # def get_redis_message(self, start_key: str, finish_key: str) -> Optional[str]:
        #     values = self.redis_client.hkeys('user:1000')
        #
        #     if finish_key in values:
        #         self.redis_client.hdel('user:1000', start_key)
        #         message = self.redis_client.hget('user:1000', finish_key)
        #     elif start_key in values:
        #         message = self.redis_client.hget('user:1000', start_key)
        #     else:
        #         message = None
        #     return message

    def get_form(self, form: Form) -> None:
        self.cache_key: str = hashlib.md5(
            f"{form.full_search_query}{form.salary_from}{form.salary_to}{form.city}{form.company}{form.remote}".encode(
                'utf-8')
        ).hexdigest()

    def get_json_vacancy(self) -> Optional[dict]:
        data: Optional[str] = self.redis_client.get(self.cache_key)
        if data is not None:
            return json.loads(data)
        return None

    def add(self, data: dict) -> None:
        self.redis_client.setex(self.cache_key, 60, json.dumps(list(data)))
        self.names_cache.append(self.cache_key)


class Cache:
    def __init__(self, connection: Redis):
        self.connection = connection


class VacancyCache(Cache):
    ...
