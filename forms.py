from validation import validate_letters_only, validate_digits_only, validate_letters_with_spaces, normalize_string, \
    is_positive_number


class VacanciesForm:
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

    def get_field(self, validators: list, title: str, value: str | None) -> str | None:
        try:
            for validator in validators:
                title = validator(title)
        except ValueError as e:
            title = None
            self.errors.append(f'Invalid {value}: {e}')
        return title

class AdminForm:
    errors: list[str] = []

    def __init__(self, form: dict) -> None:
        self.form = form

        self.auto_parser = form.get('auto_collect_vacancies')
        self.timer_auto_parser = form.get('timer1')
        self.timer_del_image = form.get('timer2')

    def validate_manual_parser(self):
        self.manual_parser = self.form.get('input_prof_name')
        try:
            normal_profession = normalize_string(self.manual_parser)
            valid_profession = validate_letters_with_spaces(normal_profession)
        except ValueError as e:
            valid_profession = None
            self.errors.append(f'Invalid manual parser: {e}')
        return valid_profession

    def validate_auto_parser(self):
        try:
            normal_profession = normalize_string(self.auto_parser)
            valid_profession = validate_letters_with_spaces(normal_profession)
        except ValueError as e:
            valid_profession = None
            self.errors.append(f'Invalid auto_parser: {e}')
        return valid_profession

    def validate_params_for_del_image(self):
        positive_number_timer, timer_digit = self.validate_timer(self.timer_del_image)
        return positive_number_timer, timer_digit

    def validate_timer(self, timer) -> tuple:
        try:
            timer_digit = validate_digits_only(timer)
            timer_digit = int(timer_digit)  # думал что здесь это команда лишняя
            is_positive_number(timer_digit)
        except ValueError as e:
            self.errors.append(f'Invalid timer: {e}')
            timer_digit = None
        return timer_digit

class AnalyticsForm:
    errors: list[str] = []

