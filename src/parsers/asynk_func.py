import asyncio

from log import logger
from parsers.easy_parser import get_data, get_average_salary, get_skills
from parsers.save_in_bd import to_bd_vacancies, to_bd_skills, to_bd_card_skills


async def process_parsing(profession) -> None:
    vacancy_data = await get_data(profession)
    vacancy_data_have_average_salary = get_average_salary(vacancy_data)
    skills, vacancy_id_and_skills = await get_skills(vacancy_data_have_average_salary)
    logger.info(f'Собраны данные по профессии {profession}')

    to_bd_vacancies(vacancy_data_have_average_salary)
    to_bd_skills(skills)
    to_bd_card_skills(vacancy_id_and_skills) # many to many
    logger.info('Сохранены в БД')


async def main_parsing(professions: str) -> None:
    professions = professions.split(',')
    tasks = [process_parsing(profession) for profession in professions]
    await asyncio.gather(*tasks)
