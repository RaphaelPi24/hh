import operator
from collections import defaultdict, Counter
from functools import reduce
from typing import List, Dict

from forms import VacanciesForm
from models import VacancyCard, Skill, VacancySkill


class Model:
    def __init__(self, form: VacanciesForm) -> None:
        self.form = form

    def get(self) -> List[Dict] | None:
        if self.form.select == 'title':
            return self.get_cards_by_title()
        elif self.form.select == 'skill':
            return self.get_cards_by_skill()
        return None

    def get_cards_by_title(self) -> List[Dict]:
        search_queries_from_words = self.form.full_search_query.split()
        conditions = [VacancyCard.name.contains(query) for query in search_queries_from_words]

        if self.form.salary_from:
            conditions.append(VacancyCard.salary_from >= int(self.form.salary_from))
        if self.form.salary_to:
            conditions.append(VacancyCard.salary_to <= int(self.form.salary_to))
        if self.form.city:
            conditions.append(VacancyCard.area == self.form.city)
        if self.form.company:
            conditions.append(VacancyCard.employer.contains(self.form.company))
        if self.form.remote == 'on':
            conditions.append(VacancyCard.schedule.contains('Удаленная работа'))

        data = (
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
            .where(*conditions)
            .dicts()
        )
        return data

    def get_cards_by_skill(self) -> List[Dict]:
        data = (
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
            .where(VacancyCard.skills.contains(self.form.full_search_query))
            .dicts()
        )
        return data


def get_popular_skills(profession):
    profession = profession.split()
    conditions = [VacancyCard.name.contains(query) for query in profession]
    data = (
        Skill
        .select(Skill.name)
        .join(VacancySkill)
        .join(VacancyCard)
        .where(*conditions)
        .dicts()
    )

    skill_counter = Counter(skill['name'] for skill in data)
    sorted_skills = sorted(skill_counter.items(), key=lambda x: x[1], reverse=False)
    return sorted_skills


def get_comparing_skills_with_salary(profession: str) -> dict:
    conditions = [VacancyCard.name.contains(query) for query in profession.split()]

    conditions.append(VacancyCard.currency == 'RUR')
    conditions.append(VacancyCard.average_salary.is_null(False))
    if conditions:
        query_conditions = reduce(operator.and_, conditions)
    else:
        query_conditions = True

    data = (
        VacancyCard
        .select(VacancyCard.average_salary, Skill.name)
        .join(VacancySkill)
        .join(Skill)
        .where(query_conditions)
        .dicts()
    )

    skills_salary = defaultdict(lambda: {"count": 0, "salary": 0})
    for entry in data:
        skill = entry['name']
        salary = entry['average_salary']
        skills_salary[skill]["count"] += 1
        skills_salary[skill]["salary"] += salary

    for skill, values in skills_salary.items():
        values["salary"] //= values["count"]

    skills_salary = dict(skills_salary)
    sorted_skills_salary = dict(
        sorted(skills_salary.items(), key=lambda item: item[1]["salary"], reverse=False)
    )
    return sorted_skills_salary
