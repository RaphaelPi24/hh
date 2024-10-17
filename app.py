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
    return render_template('views/base.html')


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
    return render_template('views/base.html', text='Всё прошло успешно')


# Поиск и отображение диаграммы с помощью HTMX
@app.route('/show_vacancies', methods=['POST'])
def get_show():
    start = time.time()
    full_search_query = request.form['user-input']
    search_queries_from_words = full_search_query.split()
    data_for_diagram = get_popular_skills()

    diagram = PopularSkillDiagramBuilder()
    image = send(diagram, data_for_diagram)

    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    cache_key = full_search_query
    cache_data = redis_client.get(cache_key)
    if cache_data:
        data_vacancies = json.loads(cache_data)
    else:
        conditions = [VacancyCard.name.contains(query) for query in search_queries_from_words]

        # Объединяем все условия с OR
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
                VacancyCard.schedule
            )
            .where(reduce(operator.or_, conditions))
            .dicts()
        )

        redis_client.setex(cache_key, 60, json.dumps(list(data_vacancies)))
    end = time.time()
    execution_time = end - start
    return render_template('views/vacancy_list.html', jobs=data_vacancies, image=image, time=execution_time)


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
            VacancyCard.schedule
        )
        .where(VacancyCard.skills.contains(search_query))
        .dicts()
    )
    return render_template('views/vacancy_list.html', jobs=data_vacancies)


if __name__ == '__main__':
    app.run()
