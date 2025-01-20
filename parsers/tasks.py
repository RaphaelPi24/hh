import asyncio


#
from parsers.asynk_func import main_parsing
#
# #
# # def process_profession_data(professions: str) -> None:
# #     asyncio.run(main_parsing(professions))
#
#
# def process_profession_data(professions: str) -> None:
#     loop = asyncio.new_event_loop()  # Создаем новый event loop
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(main_parsing(professions))
#     loop.close()  # Закрываем loop

from celery import Celery

# Создаем приложение Celery, указываем брокер сообщений (Redis)
qwe = Celery('tasks', broker='redis://localhost:6379/0')

# Настройка Celery (опционально)
qwe.conf.update(
    result_backend='redis://localhost:6379/0',  # Где сохранять результаты задач
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

# Пример задачи
@qwe.task
def process_profession_data(professions: str):
    # Импортируйте вашу функцию для парсинга
    asyncio.run(main_parsing(professions))
