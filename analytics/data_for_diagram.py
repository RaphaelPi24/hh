import operator
from collections import defaultdict
from functools import reduce

from peewee import fn

from models import VacancyCard


def get_popular_skills(profession):
    conditions = [VacancyCard.name.contains(query) for query in profession.split()]
    # Объединяем условия с оператором & (AND)
    if conditions:
        query_conditions = reduce(operator.and_, conditions)
    else:
        query_conditions = True  # Если условий нет, оставляем запрос без фильтрации

    data = (
        VacancyCard
        .select(VacancyCard.skills)
        .where(query_conditions)
        .dicts()
    )
    popular_skills = {}

    for cart in data:
        text = cart.get('skills')
        if text:
            skills_list = [skill.strip() for skill in text.split(',') if skill.strip()]
            for skill in skills_list:
                # Увеличиваем счетчик для каждого скилла
                popular_skills[skill] = popular_skills.get(skill, 0) + 1

    return popular_skills

# def get_comparing_skills_with_salary(data: list) -> dict:
    # keyskills = {}
    # for cart in data:
    #     for skill in cart.skills:
    #         if skill in keyskills:
    #             keyskills[skill]['count'] += 1
    #             if cart.get('average_salary') is not None:
    #                 # Убедись, что список зарплат существует, затем добавь зарплату
    #                 if 'salary' in keyskills[skill]:
    #                     keyskills[skill]['salary'].append(cart['average_salary'])
    #                 else:
    #                     keyskills[skill]['salary'] = [cart['average_salary']]
    #         else:
    #             keyskills[skill] = {}
    #             keyskills[skill]['count'] = 1
    #             if cart.get('average_salary') is not None:
    #                 keyskills[skill]['salary'] = [cart['average_salary']]
    #             else:
    #                 keyskills[skill]['salary'] = []
    # for key in keyskills:
    #     if len(keyskills[key]['salary']) > 0:
    #         keyskills[key]['salary'] = sum(keyskills[key]['salary']) // len(keyskills[key]['salary'])
    # return keyskills


def get_comparing_skills_with_salary(profession: str) -> dict:

    conditions = [VacancyCard.name.contains(query) for query in profession.split()]
    # Объединяем условия с оператором & (AND)
    if conditions:
        query_conditions = reduce(operator.and_, conditions)
    else:
        query_conditions = True  # Если условий нет, оставляем запрос без фильтрации

    data = (
        VacancyCard
        .select(VacancyCard.skills, VacancyCard.average_salary)
        .where(query_conditions)
        .dicts()
    )

    keyskills = defaultdict(lambda: {"count": 0, "salary": []})

    for cart in data:
        if cart.get('skills') is not None and cart.get('average_salary') is not None:
            for skill in cart.get('skills').split(','):
                # Увеличиваем счетчик
                keyskills[skill]['count'] += 1

                # Добавляем зарплату
                keyskills[skill]['salary'].append(cart['average_salary'])

    # Рассчитываем среднюю зарплату для каждого навыка
    for skill, values in keyskills.items():
        if values['salary']:
            values['salary'] = sum(values['salary']) // len(values['salary'])
        else:
            values['salary'] = 0  # Или оставьте пустым, если хотите сохранить пустой список

    return dict(keyskills)