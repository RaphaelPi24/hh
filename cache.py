import hashlib
import json
from pathlib import Path

from redis import Redis

from forms import VacanciesForm


class Cache:
    redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)


class CacheSessionPathImage(Cache):
    time_cache_images = 60

    def get_pathfile_for_profession(self, profession: str) -> str:
        if profession:
            path = self.redis_client.hget('path_image', profession)
            return path

    def get_last_entry(self) -> tuple[str | None]:
        profession = self.redis_client.hget('path_image', 'diagram')
        if profession:
            path = self.redis_client.hget('path_image', profession)
        return path, profession
        # cache должен проверять кэш, а не создавать пути из Image

    def save_path_image(self, name: str, path: str) -> None:
        if isinstance(path, Path):
            path = str(path)
        self.redis_client.setex(name, self.time_cache_images, path)
        self.redis_client.hset('path_image', 'diagram', name)


class CacheSession(Cache):
    def set_message(self, key: str, value: str) -> None:
        self.redis_client.hset('message', key, value)

    def get_session_message(self, start_key: str, finish_key: str) -> str | None:
        keys = self.redis_client.hkeys('message')

        if finish_key in keys:
            self.redis_client.hdel('message', start_key)
            message = self.redis_client.hget('message', finish_key)
            if message is not None:
                self.redis_client.hdel('message', finish_key)
        elif start_key in keys:
            message = self.redis_client.hget('message', start_key)
        else:
            message = None
        return message # может в этой функции использовать return-ы?

    def get_message_autocollect(self):
        return self.get_session_message('start_autocollection', 'finish_autocollection')

    def get_message_del_image(self):
        return self.get_session_message('start_delete_images', 'finish_delete_images')


class VacancyCache(Cache):
    names_cache: list[str] = []
    cache_key = None

    def get_form(self, form: VacanciesForm) -> None:
        self.cache_key = hashlib.md5(
            f"{form.full_search_query}{form.salary_from}{form.salary_to}{form.city}{form.company}{form.remote}".encode(
                'utf-8')
        ).hexdigest()

    def get_json_vacancy(self) -> dict | None:
        data = self.redis_client.get(self.cache_key)
        if data is not None:
            return json.loads(data)
        return None

    def add(self, data: dict) -> None:
        self.redis_client.setex(self.cache_key, 60, json.dumps(list(data)))
        self.names_cache.append(self.cache_key)
