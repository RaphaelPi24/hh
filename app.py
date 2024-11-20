import asyncio
import base64
import hashlib
import json
import os
import time
from collections.abc import Callable
from typing import Union

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, url_for, redirect, session

from analytics.data_for_diagram import get_popular_skills, get_comparing_skills_with_salary
from analytics.diagrams import PopularSkillDiagramBuilder, send, SkillsSalaryDiagramBuilder
from models import VacancyCard
from parsers.easy_parser import get_data, get_average_salary, to_bd, get_keyskills1

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
names_cache = []
schedulers = {}
app.secret_key = 'AbraKadabra5'


@app.route('/', methods=['GET'])
def get_base():
    return render_template('views/base_content.html')


def delete_images():
    print("Проверка изображений...")

    path = r"C:\papka\net\_hh\static\image_diagram"
    files = os.listdir(path)
    for file in files:
        name_file = file.split('.')[0]
        full_file_path = os.path.join(path, file)
        if name_file not in names_cache:
            try:
                os.remove(full_file_path)
                print(f'Удалено изображение: {file}')
            except Exception as e:
                print(f'Ошибка при удалении {file}: {e}')


@app.route('/admin', methods=['GET'])
def get_admin():
    # Обработка сообщений для ручного сбора
    start_autocollection = stop_autocollection = start_delete_images = stop_process_delete_images = ''
    output_for_manual_collect_vacancies = session.pop('manual_collection', None)

    # Обработка сообщений для автосбора вакансий
    if 'finish_autocollection' in session:
        session.pop('start_autocollection', None)
        stop_autocollection = session.pop('finish_autocollection')
    elif 'start_autocollection' in session:
        start_autocollection = session.get('start_autocollection')

    # Обработка сообщений для удаления изображений
    if 'finish_delete_images' in session:
        session.pop('start_delete_images', None)
        stop_process_delete_images = session.pop('finish_delete_images')
    elif 'start_delete_images' in session:
        start_delete_images = session.get('start_delete_images')

    return render_template(
        'views/admin.html',
        message_manual_collect_vacancies=output_for_manual_collect_vacancies,
        start_autocollect_vacancies=start_autocollection,
        stop_autocollection=stop_autocollection,
        start_process_delete_images=start_delete_images,
        stop_delete_images=stop_process_delete_images
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    manual_collection = request.form.get('input_prof_name') or None
    if manual_collection:
        process_profession_data(manual_collection)
        session['manual_collection'] = 'Сбор успешно завершён'
    return redirect(url_for('get_admin'))


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    automatic_collection = request.form.get('auto_collect_vacancies') or None
    timer_for_automatic_collection = request.form.get('timer1') or None
    if automatic_collection:
        professions_for_autocollection = automatic_collection.split(',')
        configuring_scheduler(timer_for_automatic_collection, process_profession_data, 'autocollection',
                              professions_for_autocollection)
        session['start_autocollection'] = 'Автосбор успешно запущен'
        # return render_template('views/admin.html', text=output1, text2=output2, text3=output3)
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    timer_for_deleting_images = request.form.get('timer2') or None
    if timer_for_deleting_images:
        configuring_scheduler(timer_for_deleting_images, delete_images, id='delete_images')
        session['start_delete_images'] = 'Автоудаление картинок успешно запущено'
    return redirect(url_for('get_admin'))


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    stop_scheduler('autocollection')
    session['finish_autocollection'] = 'Автосбор остановлен'
    return redirect(url_for('get_admin'))


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    stop_scheduler('delete_images')
    session['finish_delete_images'] = 'Автоудаление картинок остановлено'
    return redirect(url_for('get_admin'))


# куда эту ф? самый верхний уровень парсера и запись в бд
def process_profession_data(professions: [list, str]) -> None:
    if isinstance(professions, str):
        professions = [professions]
    for profession in professions:
        vacancy_data = asyncio.run(get_data(profession))
        print('Первичные данные собраны')
        # а тебя куда?
        vacancy_data_have_average_salary = get_average_salary(vacancy_data)
        print('Высчитаны данные вакансий со средними зарплатами')
        full_vacancy_data = asyncio.run(get_keyskills1(vacancy_data_have_average_salary))
        print('Собраны полные данные')
        to_bd(full_vacancy_data)
        print(f'Собраны данные по профессии {profession}')


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

    cache_key = hashlib.md5(
        f"{full_search_query}{salary_from}{salary_to}{city}{company}{remote}".encode('utf-8')
    ).hexdigest()
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
                conditions.append(VacancyCard.schedule.contains('Удаленная работа'))

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
    # jobs передается пустой, но не пустой
    return render_template('views/vacancies_cards.html', jobs=enumerate(data_vacancies, 1), time=execution_time)


#
# @app.route('/search_by_skills', methods=['POST'])
# def search_by_skills():
#     search_query = request.form['skill-input']
#     data_vacancies = (
#         VacancyCard
#         .select(
#             VacancyCard.name,
#             VacancyCard.employer,
#             VacancyCard.salary_from,
#             VacancyCard.salary_to,
#             VacancyCard.currency,
#             VacancyCard.experience,
#             VacancyCard.employment,
#             VacancyCard.schedule,
#             VacancyCard.url
#         )
#         .where(VacancyCard.skills.contains(search_query))
#         .dicts()
#     )
#     return render_template('views/vacancies_cards.html', jobs=data_vacancies)


@app.route('/vacancies', methods=['GET'])
def get_page_vacancies():
    return render_template('views/filter_vacancies.html')


@app.route('/analytics', methods=['GET'])
def get_analytics():
    return render_template('views/analytics.html')


@app.route('/analytics', methods=['POST'])
def post_analytics():
    profession = request.form.get('profession') or None
    profession2 = request.form.get('profession_stats') or None
    data_for_diagram = diagram = None
    cache_path = cache_key = None

    if profession is not None:
        cache_key = profession
        cache_path = redis_client.get(cache_key)
        if not cache_path:
            data_for_diagram = get_popular_skills(profession)
            diagram = PopularSkillDiagramBuilder()
    elif profession2 is not None:
        cache_key = profession2
        cache_path = redis_client.get(profession2)
        if not cache_path:
            data_for_diagram = get_comparing_skills_with_salary(profession2)
            diagram = SkillsSalaryDiagramBuilder()

    if cache_path:
        if isinstance(cache_path, bytes):
            image_path = cache_path.decode('utf-8')
        else:
            # Если это уже строка, используем как есть
            image_path = cache_path

    else:
        image = base64.b64decode(send(diagram, data_for_diagram))
        filename = f'static/image_diagram/{cache_key}.png'
        with open(filename, 'wb') as f:
            f.write(image)
        redis_client.setex(cache_key, 60, filename)
        image_path = filename

    return render_template('views/diagram.html', image_path=image_path)


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
        print(f'Планировщик с id - {id} отключён')
    else:
        print("Планировщик с таким идентификатором не найден.")


if __name__ == '__main__':
    app.run()
