import requests
from dataclasses import dataclass, field

url = 'https://api.hh.ru/vacancies'
head = {'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}


@dataclass
class WorkCart:
    number: int
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


    def get(self, key, default=None):
        return getattr(self, key, default)


def get_data(profession):
    params = {
        'clusters': 'true',
        'only_with_salary': 'true',
        'enable_snippets': 'true',
        'st': 'searchVacancy',
        'text': profession,
        'search_field': 'name',
        'per_page': 100,
    }
    data_json = requests.get(url, headers=head, params=params, timeout=5).json()

    jobs = []
    for i, value in enumerate(data_json['items'], 1):
        cart = WorkCart(
            number=i,
            name=value['name'],
            salary_from=value['salary']['from'],
            salary_to=value['salary']['to'],
            area=value['area']['name'],
            currency=value['salary']['currency'],
            employer=value['employer']['name'],
            schedule=value['schedule']['name'],
            experience=value['experience']['name'],
            employment=value['employment']['name'],
            api_url=value['alternate_url'],
            url=value['url'],
        )
        jobs.append(cart)
    return jobs


def get_keyskills(data: list):
    for cart in data:
        url = cart.get('api_url')
        if url:
            query_keyskills = requests.get(url, headers=head, timeout=5).json()
        keyskills = query_keyskills.get('key_skills')
        cart.skills = [skills_dict.get('name') for skills_dict in keyskills]
    return data

def get_key_skills_salary(data: list):
    keyskills = {}
    for cart in data:
        for skill in cart.skills:
            if skill in keyskills:
                keyskills[skill]['count'] += 1
                if cart.get('average_salary') is not None:
                    # Убедись, что список зарплат существует, затем добавь зарплату
                    if 'salary' in keyskills[skill]:
                        keyskills[skill]['salary'].append(cart['average_salary'])
                    else:
                        keyskills[skill]['salary'] = [cart['average_salary']]
            else:
                keyskills[skill] = {}
                keyskills[skill]['count'] = 1
                if cart.get('average_salary') is not None:
                    keyskills[skill]['salary'] = [cart['average_salary']]
                else:
                    keyskills[skill]['salary'] = []
    for key in keyskills:
        if len(keyskills[key]['salary']) > 0:
            keyskills[key]['salary'] = sum(keyskills[key]['salary']) // len(keyskills[key]['salary'])
    return keyskills


def get_average_salary(carts):
    for cart in carts:
        if all([
            cart.get('salary_from') is not None,
            cart.get('salary_to') is not None,
            cart.get('currency') == 'RUR'
        ]):
            cart.average_salary = (cart.get('salary_from') + cart.get('salary_to')) // 2
    return carts

# cart = WorkCart
#         cart['number'] = i
#         cart['name'] = value['name']
#         cart['salary_from'] = value['salary']['from']
#         cart['salary_to'] = value['salary']['to']
#         cart['area'] = value['area']['name']
#         cart['currency'] = value['salary']['currency']
#         cart['employer'] = value['employer']['name']
#         cart['schedule'] = value['schedule']['name']
#         cart['experience'] = value['experience']['name']
#         cart['employment'] = value['employment']['name']
#         cart['api_url'] = value['alternate_url']
#         cart['url'] = value['url']
