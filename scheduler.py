import asyncio
from typing import Callable, Union, List

from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.background import BackgroundScheduler

from parsers.easy_parser import get_data, get_average_salary, get_keyskills1, to_bd, to_bd_skills


def process_profession_data(professions: [list, str]) -> None:
    professions = professions.split(',')
    if isinstance(professions, str):
        professions = [professions]
    for profession in professions:
        vacancy_data = asyncio.run(get_data(profession))
        print('Первичные данные собраны')
        # а тебя куда?
        vacancy_data_have_average_salary = get_average_salary(vacancy_data)
        print('Высчитаны данные вакансий со средними зарплатами')
        data_skills = asyncio.run(get_keyskills1(vacancy_data_have_average_salary))
        print('Собраны полные данные')
        to_bd(vacancy_data)
        to_bd_skills()
        print(f'Собраны данные по профессии {profession}')


class Scheduler:
    scheduler = BackgroundScheduler()

    def start(self, time: str, f: Callable, id: str, params: Union[List, str, None] = None) -> None:
        """Запускает планировщик и добавляет задачу."""
        self.add_job(time, f, id, params=params)
        if not self.scheduler.running:
            try:
                self.scheduler.start()
                print(f'Планировщик запущен с id - {id}')
            except SchedulerAlreadyRunningError:
                print("Планировщик уже запущен")


    def stop(self, id: str) -> None:
        try:
            self.scheduler.remove_job(id)
            print(f'Планировщик с id - {id} Отключён')
        except Exception as e:
            print(e)

    def add_job(self, time: str, f: Callable, id: str, params: Union[list, str, None] = None) -> None:
        time = int(time)
        if params is not None:
            params = [params]
        self.scheduler.add_job(func=f, trigger="interval", minutes=time, args=params, id=id)

    def check_jobs(self):
        self.scheduler.print_jobs()
