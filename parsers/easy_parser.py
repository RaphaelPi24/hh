import asyncio
from dataclasses import dataclass

import aiohttp

url = 'https://api.hh.ru/vacancies'
head = {'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
all_skills = {}


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
            data_json = await response.json()

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


async def get_skills(data: list[WorkCart]) -> tuple[set[str], dict]:
    tasks = [get_skills_from_1_cart(cart) for cart in data]
    results = await asyncio.gather(*tasks)

    aggregated_skills = set()
    vacancy_id_and_skills = {}

    for result in results:
        if result:
            for vacancy_id, skills in result.items():
                vacancy_id_and_skills[vacancy_id] = skills
                aggregated_skills.update(skills)

    return aggregated_skills, vacancy_id_and_skills


async def get_skills_from_1_cart(cart: WorkCart) -> tuple[list, dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(cart.api_url) as response:
            query_skills = await response.json()
            skills = query_skills.get('key_skills')
            skills = query_skills.get('key_skills', [])
            skills_list = [skills_dict.get('name', '').strip() for skills_dict in skills if 'name' in skills_dict]
            return {cart.vacancy_id: skills_list}


def get_average_salary(carts: list[WorkCart]) -> list[WorkCart]:
    for cart in carts:
        if (
                cart.salary_from is not None
                and cart.salary_to is not None
                and cart.currency == 'RUR'
        ):
            cart.average_salary = (cart.salary_from + cart.salary_to) // 2
    return carts
