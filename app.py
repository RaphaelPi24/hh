import asyncio
import json
import operator
import time
from functools import reduce

import redis
from flask import Flask, render_template, request

from analytics.data_for_diagram import get_popular_skills
from analytics.diagrams import PopularSkillDiagramBuilder, send
from models import VacancyCard
from parsers.easy_parser import get_data, get_average_salary, to_bd, get_keyskills1

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_base():
    return render_template('views/base_content.html')


# Сбор данных с помощью формы
@app.route('/collect_vacancies', methods=['POST'])
def collect_vacancies():
    search_query = request.form['input_prof_name']

    vacancy_data = asyncio.run(get_data(search_query))
    print('Первичные данные собраны')
    vacancy_data_have_average_salary = get_average_salary(vacancy_data)
    print('Высчитаны данные вакансий со средними зарплатами')
    full_vacancy_data = asyncio.run(get_keyskills1(vacancy_data_have_average_salary))
    print('Собраны полные данные')
    to_bd(full_vacancy_data)
    return render_template('views/admin.html', text='Всё прошло успешно')


# Поиск и отображение диаграммы с помощью HTMX
@app.route('/show_vacancies', methods=['POST'])
def get_show():
    select = request.form.get('search-type')
    full_search_query = request.form.get('main_query')
    salary_from = request.form.get('salary_from') or None
    salary_to = request.form.get('salary_to') or None
    city = request.form.get('city') or None
    company = request.form.get('company') or None
    remote = request.form.get('remote') or None # on - если отмечен.  None



    #data_for_diagram = get_popular_skills()
    #diagram = PopularSkillDiagramBuilder()
    #image = send(diagram, data_for_diagram)

    start = time.time()
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    cache_key = full_search_query + str(salary_from) + str(salary_to) + str(city) + str(company) + str(remote)
    cache_data = redis_client.get(cache_key)

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
    return render_template('views/diagram.html')


if __name__ == '__main__':
    app.run()
