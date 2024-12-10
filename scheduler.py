from typing import Callable, Union, List

from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:
    scheduler = BackgroundScheduler()

    def start(self, time: int, f: Callable, id: str, params: Union[List, str, None] = None) -> None:
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

    def add_job(self, time: int, f: Callable, id: str, params: Union[list, str, None] = None) -> None:
        if params is not None:
            params = [params]
        self.scheduler.add_job(func=f, trigger="interval", minutes=time, args=params, id=id)

    def check_jobs(self):
        self.scheduler.print_jobs()
