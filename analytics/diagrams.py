import base64
import io

from matplotlib import pyplot as plt


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
