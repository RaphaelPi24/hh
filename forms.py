from validation import validate_letters_only, validate_digits_only, validate_letters_with_spaces, normalize_string


class Form:
    errors: list[str] = []

    def __init__(self, form: dict) -> None:
        self.form = form
        self.select = self.get_search_type()
        self.full_search_query = self.get_full_search_query()
        self.salary_from = self.get_salary('salary_from')
        self.salary_to = self.get_salary('salary_to')
        self.city = self.get_city()
        self.company = self.get_company()
        self.remote = self.get_remote()

    def get_search_type(self) -> str | None:
        select = self.form.get('search-type')
        if select in {'title', 'skill'}:
            return select
        self.errors.append(f'No correct >select< {select}')
        return None

    def get_full_search_query(self) -> str | None:
        full_search_query = self.form.get('main_query')
        try:
            normal_full_search_query = normalize_string(full_search_query)
            valid_full_search_query = validate_letters_with_spaces(normal_full_search_query)
        except ValueError as e:
            self.errors.append(f'Invalid full_search_query {full_search_query}')
            valid_full_search_query = None
        return valid_full_search_query

    def get_salary(self, field_name: str) -> str | None:
        salary = self.form.get(field_name)
        try:
            normal_salary = normalize_string(salary)
            valid_salary = validate_digits_only(normal_salary)
        except ValueError as e:
            self.errors.append(f'Invalid salary: {e}')
            valid_salary = None
        return valid_salary

    def get_city(self) -> str | None:
        city = self.form.get('city')
        try:
            normal_city = normalize_string(city)
            valid_city = validate_letters_only(normal_city)
        except ValueError as e:
            self.errors.append(f'Invalid city: {e}')
            valid_city = None
        return valid_city

    def get_company(self) -> str | None:
        company = self.form.get('company')
        try:
            valid_company = normalize_string(company)
        except ValueError as e:
            self.errors.append(f'Invalid company: {e}')
            valid_company = None
        return valid_company

    def get_remote(self) -> bool | None:
        remote = self.form.get('remote')
        return True if remote == 'on' else None



