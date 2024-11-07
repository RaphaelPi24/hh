import asyncio
import json
import os
import time
from collections.abc import Callable
from typing import Union

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request

from analytics.data_for_diagram import get_popular_skills, get_comparing_skills_with_salary
from analytics.diagrams import PopularSkillDiagramBuilder, send, SkillsSalaryDiagramBuilder
from models import VacancyCard
from parsers.easy_parser import get_data, get_average_salary, to_bd, get_keyskills1

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
names_cache = []
schedulers = {}


@app.route('/', methods=['GET'])
def get_base():
    return render_template('views/base_content.html')


def check_images():
    print("Проверка изображений...")

    path = r"C:\papka\net\_hh\static\image_diagram"
    files = os.listdir(path)
    del_list = []
    for file in files:
        name_file = file.split(".")[0]
        for name_cache in names_cache:
            if name_file == name_cache:
                del_list.append(file)
    for file in del_list:
        names_cache.remove(file)
        os.remove(file)


# Сбор данных с помощью формы
@app.route('/admin', methods=['POST'])
def collect_vacancies():
    manual_collection = request.form.get('input_prof_name') or None
    automatic_collection = request.form.get('auto_collect_vacancies') or None
    timer_for_automatic_collection = request.form.get('timer1') or None
    timer_for_deleting_images = request.form.get('timer2') or None
    text = text2 = text3 = ''
    if manual_collection:
        process_profession_data(manual_collection)
        text = 'Сбор успешно завершён'
    elif automatic_collection:
        text2 = 'Автосбор успешно запущен'
        professions_for_autocollection = automatic_collection.split(',')
        configuring_scheduler(timer_for_automatic_collection, process_profession_data, 'autocollection',
                              professions_for_autocollection)

    elif timer_for_deleting_images:
        text3 = 'Таймер успешно запущен'
        configuring_scheduler(timer_for_deleting_images, check_images, id='delete_images')
    return render_template('views/admin.html', text=text, text2=text2, text3=text3)


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    stop_scheduler('autocollection')
    return render_template('views/admin.html', stop_autocollection='Автосбор остановлен')


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    stop_scheduler('delete_images')
    return render_template('views/admin.html', stop_delete_images='Автоудаление картинок остановлено')


def process_profession_data(professions: [list, str]) -> None:
    if isinstance(professions, str):
        professions = [professions]
    for profession in professions:
        vacancy_data = asyncio.run(get_data(profession))
        print('Первичные данные собраны')
        vacancy_data_have_average_salary = get_average_salary(vacancy_data)
        print('Высчитаны данные вакансий со средними зарплатами')
        full_vacancy_data = asyncio.run(get_keyskills1(vacancy_data_have_average_salary))
        print('Собраны полные данные')
        to_bd(full_vacancy_data)
        print(f'Собраны данные по профессии {profession}')


# Поиск и отображение диаграммы с помощью HTMX
@app.route('/show_vacancies', methods=['POST'])
def get_show():
    select = request.form.get('search-type')
    full_search_query = request.form.get('main_query')
    salary_from = request.form.get('salary_from') or None
    salary_to = request.form.get('salary_to') or None
    city = request.form.get('city') or None
    company = request.form.get('company') or None
    remote = request.form.get('remote') or None  # on - если отмечен.  None

    start = time.time()

    cache_key = full_search_query + str(salary_from) + str(salary_to) + str(city) + str(company) + str(remote)
    cache_data = redis_client.get(cache_key)
    names_cache.append(cache_key)
    if cache_data:
        data_vacancies = json.loads(cache_data)
    else:
        if select == 'title':
            search_queries_from_words = full_search_query.split()
            conditions = [VacancyCard.name.contains(query) for query in search_queries_from_words]

            # Добавляем фильтр по зарплате (если значения указаны)
            if salary_from:
                conditions.append(VacancyCard.salary_from >= int(salary_from))
            if salary_to:
                conditions.append(VacancyCard.salary_to <= int(salary_to))

            # Добавляем фильтр по городу (если указан)
            if city:
                conditions.append(VacancyCard.area == city)

            # Добавляем фильтр по компании (если указана)
            if company:
                conditions.append(VacancyCard.employer.contains(company))

            # Добавляем фильтр по удаленной работе (если включен чекбокс)
            if remote == 'on':
                conditions.append(VacancyCard.schedule.contains('Remote'))

            # Объединяем все условия с AND (если нужно OR - используйте reduce(operator.or_, conditions))
            data_vacancies = list(
                VacancyCard
                .select(
                    VacancyCard.name,
                    VacancyCard.employer,
                    VacancyCard.salary_from,
                    VacancyCard.salary_to,
                    VacancyCard.currency,
                    VacancyCard.experience,
                    VacancyCard.employment,
                    VacancyCard.schedule,
                    VacancyCard.url
                )
                .where(*conditions)  # Применяем все условия
                .dicts()
            )

        elif select == 'skill':
            data_vacancies = (
                VacancyCard
                .select(
                    VacancyCard.name,
                    VacancyCard.employer,
                    VacancyCard.salary_from,
                    VacancyCard.salary_to,
                    VacancyCard.currency,
                    VacancyCard.experience,
                    VacancyCard.employment,
                    VacancyCard.schedule,
                    VacancyCard.url
                )
                .where(VacancyCard.skills.contains(full_search_query))
                .dicts()
            )

        redis_client.setex(cache_key, 60, json.dumps(list(data_vacancies)))
    end = time.time()
    execution_time = end - start
    return render_template('views/vacancies_cards.html', jobs=enumerate(data_vacancies, 1), time=execution_time)


@app.route('/search_by_skills', methods=['POST'])
def search_by_skills():
    search_query = request.form['skill-input']
    data_vacancies = (
        VacancyCard
        .select(
            VacancyCard.name,
            VacancyCard.employer,
            VacancyCard.salary_from,
            VacancyCard.salary_to,
            VacancyCard.currency,
            VacancyCard.experience,
            VacancyCard.employment,
            VacancyCard.schedule,
            VacancyCard.url
        )
        .where(VacancyCard.skills.contains(search_query))
        .dicts()
    )
    return render_template('views/vacancies_cards.html', jobs=data_vacancies)


@app.route('/vacancies', methods=['GET'])
def get_page_vacancies():
    return render_template('views/filter_vacancies.html')


@app.route('/admin', methods=['GET'])
def get_admin():
    return render_template('views/admin.html')


@app.route('/analytics', methods=['GET'])
def get_analytics():
    return render_template('views/analytics.html')


@app.route('/analytics', methods=['POST'])
def post_analytics():
    profession = request.form.get('profession') or None
    profession2 = request.form.get('profession_stats') or None
    if profession is not None:
        data_for_diagram = get_popular_skills(profession)
        diagram = PopularSkillDiagramBuilder()
    elif profession2 is not None:
        data_for_diagram = get_comparing_skills_with_salary(profession2)
        diagram = SkillsSalaryDiagramBuilder()
    image = send(diagram, data_for_diagram)
    return render_template('views/diagram.html', image=image)


# Настройка планировщика
def configuring_scheduler(time: str, f: Callable, id: str, params: Union[list, str, None] = None) -> None:
    time = int(time)
    if params is not None:
        params = [params]
    # job_id = str(uuid.uuid4())
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=f, trigger="interval", minutes=time, args=params, id=id)
    scheduler.start()
    schedulers[id] = scheduler


def stop_scheduler(id: str) -> None:
    if id in schedulers:
        schedulers[id].shutdown()
        del schedulers[id]
    else:
        print("Планировщик с таким идентификатором не найден.")


if __name__ == '__main__':
    app.run()
