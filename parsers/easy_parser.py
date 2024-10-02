import base64
import io

import requests
from matplotlib import pyplot as plt

head = {'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

def get_data(profession):
    url = 'https://api.hh.ru/vacancies'

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

        cart = {}
        cart['number'] = i
        cart['name'] = value['name']
        cart['salary_from'] = value['salary']['from']
        cart['salary_to'] = value['salary']['to']
        cart['currency'] = value['salary']['currency']
        cart['employer'] = value['employer']['name']
        cart['schedule'] = value['schedule']['name']
        cart['experience'] = value['experience']['name']
        cart['employment'] = value['employment']['name']
        cart['url'] = value['url']

        jobs.append(cart)
    return jobs


def get_keyskills(data: list):

    keyskills = {}
    for cart in data:
        url = cart.get('url')

        if url:
            query_keyskills = requests.get(url, headers=head, timeout=5).json()
        keyskills_1_cart = query_keyskills.get('key_skills')
        cart['skills'] = [skills_dict.get('name') for skills_dict in keyskills_1_cart]

        for skills_dict in keyskills_1_cart:
            skill = skills_dict.get('name')
            # text = ['Работа с возражениями', 'Адекватность', 'Мотивация', 'Ведение переписки']
            # if skill in text:
            #     print(cart.get('number'))
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
        #keyskills[key]['salary'] = [dec for dec in keyskills[key]['salary'] if dec is not None]
        if len(keyskills[key]['salary']) > 0:
            keyskills[key]['salary'] = sum(keyskills[key]['salary']) // len(keyskills[key]['salary'])


    return keyskills



def create_diagram_popular_skills(data):
    # Генерация диаграммы
    sorted_data = sorted(data.items(), key=lambda x: x[1])  # Сортировка по возрастанию
    #sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)  # Сортировка по убыванию

        # Разделение на метки и значения после сортировки
    labels, values = zip(*sorted_data)

    img = io.BytesIO()

    #labels = list(data.keys())
    #values = list(data.values())

    plt.figure(figsize=(10, 30))
    plt.barh(labels, values, color='skyblue')
    plt.xlabel('Количество')
    plt.title('Диаграмма навыков')
    plt.tight_layout()

    # Сохранение диаграммы в буфер
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url

#
# def create_diagram(data):
#     # Генерация диаграммы
#     img = io.BytesIO()
#
#     labels = list(data.keys())
#     values = list(data.values())
#
#     plt.figure(figsize=(12, 8))  # Увеличение размера диаграммы
#     plt.barh(labels, values, color='skyblue')
#     plt.xlabel('Количество')
#     plt.title('Диаграмма навыков')
#
#     # Повернуть подписи и уменьшить шрифт
#     plt.yticks(rotation=0, ha='right', fontsize=10)
#
#     # Автоматическая корректировка отступов
#     plt.tight_layout()
#
#     # Сохранение диаграммы в буфер
#     plt.savefig(img, format='png')
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode('utf8')
#
#     return plot_url


def get_average_salary_for_skill(carts):
    for cart in carts:
        if cart.get('salary_from') is None or cart.get('salary_to') is None:
            continue
        cart['average_salary'] = (cart.get('salary_from') + cart.get('salary_to')) // 2
    return carts


def create_diagramm_skills_salary(data):
    # Преобразование данных в списки
    # Фильтрация данных с ненулевой зарплатой

    for k in data.keys():
        if isinstance(data[k]['salary'], list):
            data[k]['salary'] = 0
    data = {k: v for k, v in data.items() if isinstance(v['salary'], (int, float)) and v['salary'] >= 0}
    # Сортировка по зарплате в порядке убывания
    data = dict(sorted(data.items(), key=lambda x: x[1]['salary'], reverse=False))

    labels = list(data.keys())
    counts = [d['count'] for d in data.values()]
    salaries = [d['salary'] for d in data.values()]

    # Создание диаграммы
    fig, ax1 = plt.subplots(figsize=(12, 30))

    # Столбцы по количеству
    ax1.barh(labels, counts, color='skyblue', label='Количество навыков')
    ax1.set_xlabel('Количество')
    ax1.set_ylabel('Навыки')
    ax1.set_title('Навыки и их количество')

    # Добавление данных о зарплатах
    for i, (count, salary) in enumerate(zip(counts, salaries)):
        ax1.text(count, i, f'{salary}', va='center')

    plt.tight_layout()

    # Сохранение диаграммы в изображение
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Конвертирование изображения в base64 для HTML
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url