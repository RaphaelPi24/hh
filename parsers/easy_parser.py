import asyncio
from dataclasses import dataclass

import aiohttp
import requests
from peewee import OperationalError, IntegrityError

from models import VacancyCard

url = 'https://api.hh.ru/vacancies'
head = {'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}


@dataclass
class WorkCart:
    vacancy_id: int
    name: str
    salary_from: int | None
    salary_to: int | None
    area: str
    currency: str
    employer: str
    schedule: str
    experience: str
    employment: str
    api_url: str
    url: str
    skills: str = None
    average_salary: int = None


def clean_decoding(string):
    return string.encode('cp1251', errors='ignore').decode('cp1251')


async def get_data(profession) -> list[WorkCart]:
    params = {
        'clusters': 'true',
        'only_with_salary': 'true',
        'enable_snippets': 'true',
        'st': 'searchVacancy',
        'text': profession,
        'search_field': 'name',
        'per_page': 100,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=head, params=params, timeout=5) as response:
            data_json = await response.json()  # Асинхронное получение JSON

    jobs = []
    for i, value in enumerate(data_json['items'], 1):
        cart = WorkCart(
            vacancy_id=value['id'],
            name=clean_decoding(value['name']),
            salary_from=value['salary']['from'],
            salary_to=value['salary']['to'],
            area=value['area']['name'],
            currency=value['salary']['currency'],
            employer=value['employer']['name'],
            schedule=value['schedule']['name'],
            experience=value['experience']['name'],
            employment=value['employment']['name'],
            api_url=value['url'],
            url=value['alternate_url'],
        )
        jobs.append(cart)
    return jobs


def get_keyskills(data: list[WorkCart]) -> list[WorkCart]:
    for cart in data:
        url = cart.api_url
        if url:
            query_keyskills = requests.get(url, headers=head, timeout=5).json()
        keyskills = query_keyskills.get_json_vacancy('key_skills')
        skills_list = [skills_dict.get_json_vacancy('name') for skills_dict in keyskills]
        cart.skills = ','.join(skills_list)
    return data


async def get_keyskills1(data: list[WorkCart]) -> tuple[WorkCart]:
    # Используем asyncio.gather для асинхронного вызова get_skills_from_1_cart для каждого элемента
    tasks = [get_skills_from_1_cart(cart) for cart in data]

    # Ожидаем завершения всех задач
    data_with_skills = await asyncio.gather(*tasks)

    return data_with_skills


async def get_skills_from_1_cart(cart: WorkCart) -> WorkCart:
    async with aiohttp.ClientSession() as session:
        async with session.get(cart.api_url) as response:
            query_skills = await response.json()
            skills = query_skills.get_json_vacancy('key_skills')
            if skills is not None:
                skills_list = [skills_dict.get_json_vacancy('name') for skills_dict in skills]
                cart.skills = ','.join(skills_list)
    return cart

def get_average_salary(carts: list[WorkCart]) -> list[WorkCart]:
    for cart in carts:
        if (
            cart.salary_from is not None
            and cart.salary_to is not None
            and cart.currency == 'RUR'
        ):
            cart.average_salary = (cart.salary_from + cart.salary_to) // 2
    return carts


def to_bd(data: tuple[WorkCart]) -> None:
    try:
        VacancyCard.create_table()
    except OperationalError:
        print("Таблица VacancyCard уже существует.")
    for cart in data:
        try:
            print(cart)
            # Используем get_or_create для предотвращения дублирования по cart_id
            vacancy_card, created = VacancyCard.get_or_create(
                vacancy_id=cart.vacancy_id,  # Проверяем уникальный ID вакансии
                defaults={
                    'name': cart.name,
                    'salary_from': cart.salary_from,
                    'salary_to': cart.salary_to,
                    'area': cart.area,
                    'currency': cart.currency,
                    'employer': cart.employer,
                    'schedule': cart.schedule,
                    'experience': cart.experience,
                    'employment': cart.employment,
                    'api_url': cart.api_url,
                    'url': cart.url,
                    'skills': cart.skills,
                    'average_salary': cart.average_salary
                }
            )

            if created:
                print(f"Vacancy {cart.name} added successfully.")
            else:
                print(f"Vacancy {cart.name} already exists.")
        except IntegrityError as e:
            print(f"Error saving vacancy: {e}")
