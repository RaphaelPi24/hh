from peewee import IntegrityError

from models import VacancyCard, Skill, VacancySkill
from parsers.easy_parser import WorkCart


def to_bd_vacancies(data: tuple[WorkCart]) -> None:
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


def to_bd_skills(data :set) -> None:
    query = [Skill(name=skill) for skill in data]
    try:
        with Skill._meta.database.atomic():
            Skill.bulk_create(query)
    except IntegrityError as e:
        print(f'Не получилось записать умения в Таблицу Skill {e}')


def to_bd_card_skills(vacancy_data: dict) -> None:
    existing_vacancy_ids = {vacancy["vacancy_id"] for vacancy in VacancyCard.select(VacancyCard.vacancy_id).dicts()}
    skills_map = {skill.name: skill.id for skill in Skill.select(Skill.id, Skill.name)}
    cards_skills = []

    for vacancy_id, skills in vacancy_data.items():
        if vacancy_id in existing_vacancy_ids:
            for skill_name in skills:
                skill_name = skill_name.strip()
                if skill_name in skills_map:
                    id_cart_from_vacancy_card = VacancyCard.get(VacancyCard.vacancy_id == vacancy_id).id
                    id_skill_from_skill = skills_map[skill_name]
                    cards_skills.append(
                        VacancySkill(vacancy_id=id_cart_from_vacancy_card, skill_id=id_skill_from_skill))

    try:
        with VacancySkill._meta.database.atomic():
            VacancySkill.bulk_create(cards_skills)
    except IntegrityError as e:
        print(f'Не получилось вставить Vacancy Skill {e}')