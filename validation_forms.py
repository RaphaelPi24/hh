import re
from typing import Optional

from redis import Redis


# Optional - для значений вместе c None
class Form:
    errors: list[str] = []

    def __init__(self, form: dict) -> None:
        self.form = form
        self.select: str | None = self.get_search_type()
        self.full_search_query: Optional[str] = self.get_full_search_query()
        self.salary_from: Optional[str] = self.get_salary('salary_from')
        self.salary_to: Optional[str] = self.get_salary('salary_to')
        self.city: Optional[str] = self.get_city()
        self.company: Optional[str] = self.get_company()
        self.remote: Optional[bool] = self.get_remote()

    def get_search_type(self) -> Optional[str]:
        select: Optional[str] = self.form.get('search-type')
        if select in {'title', 'skill'}:
            return select
        self.errors.append(f'No correct >select< {select}')
        return None

    def get_full_search_query(self) -> Optional[str]:
        full_search_query = self.form.get('main_query', '').strip()
        if re.fullmatch(r"[A-Za-zА-Яа-яЁё ]+", full_search_query):
            return full_search_query
        self.errors.append(f'No correct >full_search_query< {full_search_query}')
        return None

    def get_salary(self, field_name: str) -> Optional[str]:
        salary: Optional[str] = self.form.get(field_name)
        if salary and len(salary) > 0:
            if salary.strip().isdigit():
                return salary.strip()
            else:
                self.errors.append(f'No correct >{field_name}< {salary}')
        return None

    def get_city(self) -> Optional[str]:
        city: Optional[str] = self.form.get('city')
        if city and len(city) > 0:
            city = city.strip()
            if city.isalpha():
                return city
            else:
                self.errors.append(f'No correct >city< {city}')
        return None

    def get_company(self) -> Optional[str]:
        company: Optional[str] = self.form.get('company')
        if company and len(company) > 0:
            return company.strip()
        return None

    def get_remote(self) -> Optional[bool]:
        remote: Optional[str] = self.form.get('remote')
        if remote == 'on':
            return True
        return None



